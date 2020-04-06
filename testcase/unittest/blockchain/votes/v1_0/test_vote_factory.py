import os

import pytest

from loopchain.blockchain.blocks.v1_0.block import Block, BlockHeader, BlockBody
from loopchain.blockchain.invoke_result import InvokeResult, InvokeResultPool
from loopchain.blockchain.types import Hash32, ExternalAddress, Signature, BloomFilter
from loopchain.blockchain.votes.v1_0 import BlockVote, BlockVoteFactory
from loopchain.crypto.signature import Signer


class TestVoteFactory:
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

    @pytest.fixture
    def invoke_pool(self) -> InvokeResultPool:
        return InvokeResultPool()

    @pytest.mark.asyncio
    async def test_create_vote(self, invoke_pool):
        # GIVEN I have a Block
        commit_id = Hash32(os.urandom(Hash32.size))
        epoch_num = 1
        round_num = 1
        header = BlockHeader(
            hash=self.DATA_ID,
            prev_hash=Hash32.new(),
            height=1,
            timestamp=1,
            peer_id=ExternalAddress.new(),
            signature=Signature.new(),
            epoch=epoch_num,
            round=round_num,
            validators_hash=Hash32.new(),
            next_validators_hash=Hash32.new(),
            prev_votes_hash=Hash32.new(),
            transactions_hash=Hash32.new(),
            prev_state_hash=Hash32.new(),
            prev_receipts_hash=Hash32.new(),
            prev_logs_bloom=BloomFilter.new()
        )
        body = BlockBody(
            transactions=["a"],
            prev_votes=""
        )
        block: Block = Block(header=header, body=body)

        invoke_result = InvokeResult(block, self.InvokeResultDict)
        invoke_pool.add_message(invoke_result)

        # AND I Made VoteFactory
        signer = Signer.new()
        vote_factory: BlockVoteFactory = BlockVoteFactory(
            invoke_result_pool=invoke_pool,
            signer=signer
        )

        # WHEN I create vote
        vote: BlockVote = await vote_factory.create_vote(
            data_id=self.DATA_ID,
            commit_id=commit_id,
            epoch_num=epoch_num,
            round_num=round_num
        )

        # THEN The vote should have valid hash
        assert vote.hash and vote.hash != Hash32.new()

        # AND The vote should be real vote
        assert vote.is_real()
        assert not vote.is_none()
        assert not vote.is_lazy()

    @pytest.mark.asyncio
    async def test_lazy_vote(self, invoke_pool):
        # GIVEN I Made VoteFactory
        signer = Signer.new()
        vote_factory: BlockVoteFactory = BlockVoteFactory(
            invoke_result_pool=invoke_pool,
            signer=signer
        )

        # WHEN I create none vote
        vote: BlockVote = vote_factory.create_lazy_vote(
            voter_id=ExternalAddress(os.urandom(ExternalAddress.size)),
            epoch_num=1,
            round_num=1
        )

        # THEN The factory should be a none vote
        assert not vote.is_real()
        assert not vote.is_none()
        assert vote.is_lazy()

    @pytest.mark.asyncio
    async def test_none_vote(self, invoke_pool):
        # GIVEN I Made VoteFactory
        signer = Signer.new()
        vote_factory: BlockVoteFactory = BlockVoteFactory(
            invoke_result_pool=invoke_pool,
            signer=signer
        )

        # WHEN I create none vote
        vote: BlockVote = vote_factory.create_none_vote(
            epoch_num=1,
            round_num=1
        )

        # THEN The factory should be a none vote
        assert vote.is_real()
        assert vote.is_none()
        assert not vote.is_lazy()
