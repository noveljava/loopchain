# Copyright 2018-current ICON Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""block builder for version 0.5 block"""

from loopchain.blockchain.blocks import BlockProverType
from loopchain.blockchain.blocks import BlockBuilder as BaseBlockBuilder
from loopchain.blockchain.blocks.v0_5 import BlockProver
from loopchain.blockchain.blocks.v1_0.block import Block, BlockHeader, BlockBody
from loopchain.blockchain.types import Hash32


class BlockBuilder(BaseBlockBuilder):
    version = BlockHeader.version
    BlockHeaderClass = BlockHeader
    BlockBodyClass = BlockBody

    def build(self) -> 'Block':
        validators_hash = self._last_block.header.validators_hash
        next_validators_hash = invoke_result.next_reps_hash
        prev_votes_hash = prev_votes  # FIXME: get root hash
        prev_state_hash = prev_votes[0].state_hash  # FIXME
        prev_receipts_hash = self._last_block.body.transactions  # FIXME: get root hash
        prev_logs_bloom = transactions  # FIXME: get logs_bloom

        hash_: Hash32 = Hash32.new()  # FIXME: hash of the block
        signature: 'Signature' = Signature.new()

        body = BlockBody(
            transactions=transactions,
            prev_votes=prev_votes
        )

        header = BlockHeader(
            hash=hash_,
            prev_hash=prev_id,
            height=data_number,
            timestamp=timestamp,
            peer_id=peer_id,
            signature=signature,
            epoch=epoch_num,
            round=round_num,
            validators_hash=validators_hash,
            next_validators_hash=next_validators_hash,
            prev_votes_hash=prev_votes_hash,
            transactions_hash=transactions_hash,
            prev_state_hash=prev_state_hash,
            prev_receipts_hash=prev_receipts_hash,
            prev_logs_bloom=prev_logs_bloom
        )

        return Block(
            header=header,
            body=body
        )

    def build_block_header_data(self) -> dict:
        pass

    def build_block_body_data(self) -> dict:
        pass

    def _build_hash(self):
        pass

    def _build_transactions_hash(self):
        if not self.transactions:
            return Hash32.empty()

        block_prover = BlockProver(self.transactions.keys(), BlockProverType.Transaction)
        return block_prover.get_proof_root()
