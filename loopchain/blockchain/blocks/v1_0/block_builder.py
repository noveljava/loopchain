"""block builder for version 1.0 block"""
import time
from functools import reduce
from operator import or_
from typing import List, Optional

from loopchain.blockchain.blocks import BlockProverType
from loopchain.blockchain.blocks import NextRepsChangeReason, BlockBuilder as BaseBlockBuilder
from loopchain.blockchain.blocks.v0_3 import BlockProver
from loopchain.blockchain.blocks.v1_0.block import Block, BlockHeader, BlockBody
from loopchain.blockchain.transactions import TransactionVersioner
from loopchain.blockchain.types import ExternalAddress, BloomFilter, Hash32
from loopchain.blockchain.votes.v1_0 import BlockVote


class BlockBuilder(BaseBlockBuilder):
    version = BlockHeader.version
    BlockHeaderClass = BlockHeader
    BlockBodyClass = BlockBody

    def __init__(self, tx_versioner: 'TransactionVersioner'):
        super().__init__(tx_versioner)

        # Attributes that must be assigned
        self.validators: Optional[List[ExternalAddress]] = None
        self.next_validators: Optional[List[ExternalAddress]] = None
        self.next_validators_hash: Optional[Hash32] = None
        self.next_validators_change_reason: NextRepsChangeReason = NextRepsChangeReason.NoChange
        self.prev_votes: Optional[List[BlockVote]] = None
        self.epoch: Optional[int] = None
        self.round: Optional[int] = None

        # Attributes to be assigned(optional)
        self.fixed_timestamp: Optional[int] = None
        self.is_max_made_block_count: Optional[bool] = None

        # Attributes to be generated
        self.prev_votes_hash: Optional[Hash32] = None
        self.transactions_hash: Optional[Hash32] = None
        self.prev_state_hash: Optional[Hash32] = None
        self.prev_receipts_hash: Optional[Hash32] = None
        self.validators_hash: Optional[Hash32] = None
        self.prev_logs_bloom: Optional[BloomFilter] = None
        self._timestamp: Optional[int] = None
        self._prev_receipts: Optional[list] = None

    @property
    def prev_receipts(self):
        return self._prev_receipts

    # receipts are txResults from Iconservice
    # (see. https://docs.google.com/document/d/1WkK2foaxauqTTT-GRyOaabgjhcrPB5049Qt6GENpAnI/edit)
    # [
    #     {
    #         "status": "0x1",
    #         "txHash": "a3e227cf2513d04b5dc1ba6579132b143087c68db1b2168786408fcbce568238",
    #         "txIndex": "0x0",
    #         "blockHeight": "0x1234",
    #         "blockHash": "c71303ef8543d04b5dc1ba6579132b143087c68db1b2168786408fcbce568238",
    #         "cumulativeStepUsed": "0x1234",
    #         "stepUsed": "0x1234",
    #         "stepPrice": "0x100",
    #         "scoreAddress": "cxb0776ee37f5b45bfaea8cff1d8232fbb6122ec32"
    #     }
    # ]

    @prev_receipts.setter
    def prev_receipts(self, prev_receipts):
        self._prev_receipts = prev_receipts

        for receipt in self._prev_receipts:
            receipt.pop("blockHash", None)

    def reset_cache(self):
        # TODO In 'LFT', this method call is unnecessary. Delete after confirmation.
        super().reset_cache()

        self.prev_votes_hash = None
        self.transactions_hash = None
        self.prev_state_hash = None
        self.prev_receipts_hash = None
        self.validators_hash = None
        self.prev_logs_bloom = None
        self._timestamp = None
        self.epoch = None
        self.round = None

    def build(self) -> 'Block':
        self.build_peer_id()
        self.build_hash()
        self.sign()

        self.block = self.build_block()
        return self.block

    def build_block_header_data(self) -> dict:
        pass

    def build_block_body_data(self) -> dict:
        pass

    def build_prev_votes_hash(self):
        if self.prev_votes_hash is None:
            self.prev_votes_hash = self._build_prev_votes_hash()

        return self.prev_votes_hash

    def _build_prev_votes_hash(self):
        if not self.prev_votes:
            return Hash32.new()

        block_prover = BlockProver((vote.hash if vote else None for vote in self.prev_votes),
                                   BlockProverType.Vote)
        return block_prover.get_proof_root()

    def build_transactions_hash(self):
        if self.transactions_hash is None:
            self.transactions_hash = self._build_transactions_hash()

        return self.transactions_hash

    def _build_transactions_hash(self):
        if not self.transactions:
            return Hash32.empty()

        block_prover = BlockProver(self.transactions.keys(), BlockProverType.Transaction)
        return block_prover.get_proof_root()

    def build_prev_receipts_hash(self):
        if self.prev_receipts_hash is None:
            self.prev_receipts_hash = self._build_prev_receipts_hash()

        return self.prev_receipts_hash

    def _build_prev_receipts_hash(self):
        if not self.prev_receipts:
            return Hash32.empty()

        block_prover = BlockProver(self.prev_receipts, BlockProverType.Receipt)
        return block_prover.get_proof_root()

    def build_validators_hash(self):
        if self.validators_hash is None:
            block_prover = BlockProver((validator.extend() for validator in self.validators), BlockProverType.Rep)
            self.validators_hash = block_prover.get_proof_root()
        return self.validators_hash

    def build_next_validators_hash(self):
        if self.next_validators_hash is None:
            block_prover = BlockProver((validator.extend() for validator in self.next_validators), BlockProverType.Rep)
            self.next_validators_hash = block_prover.get_proof_root()
        return self.next_validators_hash

    def build_logs_bloom(self):
        if self.prev_logs_bloom is None:
            self.prev_logs_bloom = self._build_logs_bloom()

        return self.prev_logs_bloom

    def _build_logs_bloom(self):
        if not self.prev_receipts:
            return BloomFilter.new()

        logs_blooms = (BloomFilter.fromhex(receipt["logsBloom"])
                       for receipt in self.prev_receipts if "logsBloom" in receipt)
        return BloomFilter(reduce(or_, logs_blooms, BloomFilter.new()))

    def build_hash(self):
        if self.hash is None:
            if self.height > 0 and self.prev_hash is None:
                raise RuntimeError

            self.build_prev_votes_hash()
            self.build_transactions_hash()
            self.build_prev_receipts_hash()
            self.build_validators_hash()
            self.build_next_validators_hash()
            self.build_logs_bloom()
            self.hash = self._build_hash()

        return self.hash

    def _build_hash(self):
        if self.fixed_timestamp:
            self._timestamp = self.fixed_timestamp
        else:
            self._timestamp = int(time.time() * 1_000_000)

        leaves = (
            self.prev_hash,
            self.prev_votes_hash,
            self.transactions_hash,
            self.prev_state_hash,
            self.prev_receipts_hash,
            self.validators_hash,
            self.next_validators_hash,
            self.prev_logs_bloom,
            self.height,
            self._timestamp,
            self.peer_id,
            self.epoch,
            self.round
        )
        block_prover = BlockProver(leaves, BlockProverType.Block)
        return block_prover.get_proof_root()

    def from_(self, block: 'Block'):
        super().from_(block)

        header: BlockHeader = block.header

        self.validators_hash = header.validators_hash
        self.next_validators_hash = header.next_validators_hash
        self.epoch = header.epoch
        self.round = header.round
        self.prev_votes_hash = header.prev_votes_hash
        self.transactions_hash = header.transactions_hash
        self.prev_state_hash = header.prev_state_hash
        self.prev_receipts_hash = header.prev_receipts_hash
        self.prev_logs_bloom = header.prev_logs_bloom
        self.fixed_timestamp = header.timestamp
        self._timestamp = header.timestamp

        body: BlockBody = block.body
        self.prev_votes = body.prev_votes
