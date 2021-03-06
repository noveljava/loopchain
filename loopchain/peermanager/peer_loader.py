"""PeerListData Loader for PeerManager"""

import os

from loopchain import configure as conf
from loopchain import utils
from loopchain.baseservice import ObjectManager, RestMethod
from loopchain.blockchain.blocks import BlockProverType
from loopchain.blockchain.blocks.v0_3 import BlockProver
from loopchain.blockchain.types import ExternalAddress, Hash32
from loopchain.channel.channel_property import ChannelProperty


class PeerLoader:
    def __init__(self):
        pass

    @staticmethod
    def load():
        peers = PeerLoader._load_peers_from_db()
        if peers:
            utils.logger.info("Reps data loaded from DB")
        elif os.path.exists(conf.CHANNEL_MANAGE_DATA_PATH):
            utils.logger.info(f"Try to load reps data from {conf.CHANNEL_MANAGE_DATA_PATH}")
            peers = PeerLoader._load_peers_from_file()
        else:
            utils.logger.info("Try to load reps data from other reps")
            peers = PeerLoader._load_peers_from_rest_call()

        block_prover = BlockProver((ExternalAddress.fromhex_address(peer['id']).extend() for peer in peers),
                                   BlockProverType.Rep)
        peer_root_hash = block_prover.get_proof_root()

        return peer_root_hash, peers

    @staticmethod
    def _load_peers_from_db() -> list:
        blockchain = ObjectManager().channel_service.block_manager.blockchain
        last_block = blockchain.last_block
        rep_root_hash = (last_block.header.reps_hash if last_block else
                         Hash32.fromhex(conf.CHANNEL_OPTION[ChannelProperty().name].get('crep_root_hash')))

        return blockchain.find_preps_by_roothash(rep_root_hash)

    @staticmethod
    def _load_peers_from_file():
        channel_info = utils.load_json_data(conf.CHANNEL_MANAGE_DATA_PATH)
        reps: list = channel_info[ChannelProperty().name].get("peers")
        return [{"id": rep["id"], "p2pEndpoint": rep["peer_target"]} for rep in reps]

    @staticmethod
    def _load_peers_from_rest_call():
        rs_client = ObjectManager().channel_service.rs_client
        crep_root_hash = conf.CHANNEL_OPTION[ChannelProperty().name].get('crep_root_hash')
        reps = rs_client.call(
            RestMethod.GetReps,
            RestMethod.GetReps.value.params(crep_root_hash)
        )
        return [{"id": rep["address"], "p2pEndpoint": rep["p2pEndpoint"]} for rep in reps]
