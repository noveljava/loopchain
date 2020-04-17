import time
from typing import TYPE_CHECKING, Sequence

from lft.consensus.messages.data import DataFactory

from loopchain import configure_default as conf
from loopchain import utils
from loopchain.blockchain import Hash32, TransactionStatusInQueue
from loopchain.blockchain.blocks.v1_0.block import Block, BlockHeader
from loopchain.blockchain.blocks.v1_0.block_builder import BlockBuilder
from loopchain.blockchain.blocks.v1_0.block_verifier import BlockVerifier
from loopchain.blockchain.invoke_result import InvokeResultPool
from loopchain.blockchain.transactions import Transaction, TransactionVerifier
from loopchain.crypto.signature import Signer
from loopchain.store.key_value_store import KeyValueStore

if TYPE_CHECKING:
    from loopchain.blockchain.votes.v1_0.vote import BlockVote
    from loopchain.baseservice.aging_cache import AgingCache
    from loopchain.store.key_value_store_plyvel import KeyValueStorePlyvel


class BlockFactory(DataFactory):
    NoneData = Hash32.empty()
    LazyData = Hash32(bytes([255] * 32))

    def __init__(self, peer_auth, tx_queue: 'AgingCache', db: KeyValueStore, tx_versioner, invoke_pool: InvokeResultPool, signer):
        self._peer_auth = peer_auth  # ChannelProperty
        self._tx_versioner = tx_versioner

        self._tx_queue: 'AgingCache' = tx_queue
        self._invoke_pool: InvokeResultPool = invoke_pool
        self._db: 'KeyValueStorePlyvel' = db  # TODO: Will be replaced as DB Component
        self._last_block: Block = ""  # FIXME: store it in memory or get it from db

        # From BlockBuilder
        self._signer: Signer = signer
        self._peer_id = None

    async def create_data(self, data_number: int, prev_id: bytes, epoch_num: int, round_num: int,
                          prev_votes: Sequence['BlockVote']) -> Block:
        prev_id: Hash32

        # Epoch.makeup_block
        block_builder = BlockBuilder.new(BlockHeader.version, self._tx_versioner)
        block_builder.fixed_timestamp = int(time.time() * 1_000_000)
        block_builder.prev_votes = prev_votes
        self._add_tx_to_block(block_builder)

        # ConsensusSiever.__build_candidate_block
        block_builder.height = data_number
        block_builder.prev_hash = prev_id
        block_builder.signer = self._peer_auth

        invoke_result = self._invoke_pool.invoke(
            prev_block=self._last_block,
            height=data_number,
            block_hash=prev_id,
            prev_votes=prev_votes,
            transactions=block_builder.transactions,
            timestamp=block_builder.fixed_timestamp,
            tx_versioner=self._tx_versioner,
            is_block_editable=True
        )

        # TODO: Add additional params to block_builder
        block: Block = block_builder.build()

        return block

    def _add_tx_to_block(self, block_builder: BlockBuilder):
        tx_queue: 'AgingCache' = self._tx_queue

        block_tx_size = 0
        tx_versioner = self._tx_versioner

        while tx_queue:
            if block_tx_size >= conf.MAX_TX_SIZE_IN_BLOCK:
                utils.logger.warning(
                    f"consensus_base total size({block_builder.size()}) "
                    f"count({len(block_builder.transactions)}) "
                    f"_txQueue size ({len(tx_queue)})")
                break

            tx: 'Transaction' = tx_queue.get_item_in_status(
                get_status=TransactionStatusInQueue.normal,
                set_status=TransactionStatusInQueue.added_to_block
            )
            if tx is None:
                break

            block_timestamp = block_builder.fixed_timestamp
            if not utils.is_in_time_boundary(tx.timestamp, conf.TIMESTAMP_BOUNDARY_SECOND, block_timestamp):
                utils.logger.info(f"fail add tx to block by TIMESTAMP_BOUNDARY_SECOND"
                                  f"({conf.TIMESTAMP_BOUNDARY_SECOND}) "
                                  f"tx({tx.hash}), timestamp({tx.timestamp})")
                continue

            tv = TransactionVerifier.new(tx.version, tx.type(), tx_versioner)

            try:
                # FIXME: Currently TransactionVerifier uses `Blockchain` to check uniqueness of tx.
                # FIXME: To cut the dependencies with `Blockchain`, implement related methods into db store.
                tv.verify(tx, blockchain=self._db)
            except Exception as e:
                utils.logger.warning(
                    f"tx hash invalid. tx: {tx} exception: {e}", exc_info=e)
            else:
                block_builder.transactions[tx.hash] = tx
                block_tx_size += tx.size(tx_versioner)

    def create_none_data(self, epoch_num: int, round_num: int, proposer_id: bytes) -> Block:
        pass

    def create_lazy_data(self, epoch_num: int, round_num: int, proposer_id: bytes) -> Block:
        pass

    async def create_data_verifier(self) -> BlockVerifier:
        return BlockVerifier()
