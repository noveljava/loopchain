import os

import pytest

from loopchain.blockchain import Hash32
from loopchain.blockchain.blocks import BlockHeader
from loopchain.blockchain.blocks.v1_0.block import Block, BlockHeader, BlockBody
from loopchain.blockchain.blocks.v1_0.block_factory import BlockFactory
from loopchain.blockchain.invoke_result import InvokeResult
from loopchain.blockchain.types import ExternalAddress, Signature, BloomFilter
from loopchain.blockchain.votes.v1_0 import BlockVote, BlockVoteFactory
from loopchain.crypto.signature import Signer


class TestBlockFactory:
    DATA_ID = Hash32.fromhex("c71303ef8543d04b5dc1ba6579132b143087c68db1b2168786408fcbce568238", ignore_prefix=True)
    InvokeResultDict = {
        "txResults": [
            {
                "status": "0x1",
                "txHash": "a3e227cf2513d04b5dc1ba6579132b143087c68db1b2168786408fcbce568238",
                "txIndex": "0x0",
                "blockHeight": "0x1234",
                "blockHash": DATA_ID.hex(),
                "cumulativeStepUsed": "0x1234",
                "stepUsed": "0x1234",
                "stepPrice": "0x100",
                "scoreAddress": "cxb0776ee37f5b45bfaea8cff1d8232fbb6122ec32"
            }
        ],
        "stateRootHash": "c71303ef8543d04b5dc1ba6579132b143087c68db1b2168786408fcbce568238",
        "addedTransactions": {
            "6804dd2ccd9a9d17136d687838aa09e02334cd4afa964d75993f18991ee874de": {
                "version": "0x3",
                "timestamp": "0x563a6cf330136",
                "dataType": "base",
                "data": {
                    "prep": {
                        "incentive": "0x1",
                        "rewardRate": "0x1",
                        "totalDelegation": "0x3872423746291",
                        "value": "0x7800000"
                    }
                }
            }
        },
        "prep": {
            "preps": [
                {
                    "id": "hx86aba2210918a9b116973f3c4b27c41a54d5dafe",
                    "p2pEndpoint": "123.45.67.89:7100"
                },
                {
                    "id": "hx13aca3210918a9b116973f3c4b27c41a54d5dad1",
                    "p2pEndPoint": "210.34.56.17:7100"
                }
            ],
            "irep": "0x1",
            "state": "0x0",
            "rootHash": "c7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a"
        }
    }

    @pytest.mark.asyncio
    async def test_create_data(self):
        peer_id = ExternalAddress.empty()
        tx_pool = ""
        tx_versioner = ""
        invoke_pool = ""

        block_factory = BlockFactory(peer_id, tx_pool, tx_versioner, invoke_pool)

        height = 10
        prev_hash = Hash32.new()
        block: Block = await block_factory.create_data(
            data_number=height,
            prev_id=prev_hash,
            epoch_num=1,
            round_num=1,
            prev_votes=1
        )

        assert isinstance(block, Block)
