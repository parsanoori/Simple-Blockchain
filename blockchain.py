from hashlib import sha256
import itertools


class TheresANextBlockException(Exception):
    pass


class TheresNoNextBlockException(Exception):
    pass


class Block:
    # stores the content into a string and takes it hash
    def _calculate_hash(self):
        message_to_digest = f'data:{self._data}\nprevious_block_hash:{self._previous_block_hash}'
        h = sha256()
        h.update(bytearray(message_to_digest, 'utf8'))
        self._hash = h.hexdigest()

    # a wrapper for above function
    def recalculate_hash(self) -> str:
        self._calculate_hash()
        return self._hash

    # an initializer which needs the data and the hash of the previous block
    # which is obvious why its needed in blockchain
    def __init__(self, data: [int], previous_block_hash: str):
        self._data = data
        self._next = None
        self._previous_block_hash = previous_block_hash
        self._calculate_hash()

    # getters and setters lined up
    def get_data(self) -> [int]:
        return self._data

    def set_next_block(self, block: 'Block'):
        if self._next is not None:
            raise TheresANextBlockException()
        self._next = block

    def get_next_block(self) -> 'Block':
        if self._next is None:
            raise TheresNoNextBlockException()
        return self._next

    def get_block_hash(self) -> str:
        return self._hash

    # Block hash and block data represent the block
    def __repr__(self):
        return f'Block hash: {self._hash}\nBlock data: {self._data}'


class BlockChain:
    _hashes: [str] = []

    def __init__(self):
        self._first_block: Block = None

    # its a good idea to iterate over the blockchain too reduce code duplicates
    def __iter__(self):
        block = self._first_block
        while block is not None:
            yield block
            try:
                block = block.get_next_block()
            except TheresNoNextBlockException:
                block = None

    # adds a block by iterating over the blockchain
    def add_block(self, block_data: [int]):
        if not self._first_block:
            self._first_block = Block(block_data, 'just assumed correct')
            BlockChain._hashes.append(self._first_block.get_block_hash())
            return
        current_block: Block
        for current_block in self:
            pass
        new_block = Block(block_data, current_block.get_block_hash())
        current_block.set_next_block(new_block)
        BlockChain._hashes.append(new_block.get_block_hash())

    # recalculates the hashes
    def recalculate_block_hashes(self):
        for block in self:
            block.recalculate_hash()

    # iterates over the blocks compares them with the backup
    def is_blockchain_valid(self) -> bool:
        self.recalculate_block_hashes()
        i = 0
        for block in self:
            if block.get_block_hash() != BlockChain._hashes[i]:
                return False
            i += 1
        return True

    # finds the changed block
    def changed_block(self) -> (Block, int):
        i = 0
        for block in self:
            if block.get_block_hash() != BlockChain._hashes[i]:
                return block, i
            i += 1
        return None

    # gets the hash from the backup
    @staticmethod
    def get_hash_for_height_in_original_blockchain(height: int):
        return BlockChain._hashes[height]


if __name__ == '__main__':
    blockchain = BlockChain()
    blockchain.add_block([1, 2, 3, 4, 5, 6, 7, 8])
    blockchain.add_block([1, 1, 2, 3, 4, 5, 6, 7])
    blockchain.add_block([1, 1, 1, 3, 4, 5, 6, 7])
    blockchain.add_block([1, 1, 1, 1, 4, 5, 6, 7])
    print(f'The blockchain\'s validity is {blockchain.is_blockchain_valid()}')

    # here's the part where the bad guys play their roles
    blockchain._first_block._next._data = [1, 2, 1, 3, 4, 5, 6, 7]
    # end of bad guys role

    # this indicates that the blockchain correctly detects thieves
    print(f'But now the blockchain\'s validity is {blockchain.is_blockchain_valid()} since thieves have modified it')
    changed_block = blockchain.changed_block()
    print(f'The changed block\' height is {changed_block[1]} and block is:\n{changed_block[0]}')

    # lets find the original version
    changed_block_data = changed_block[0].get_data()
    original_block_hash = BlockChain.get_hash_for_height_in_original_blockchain(changed_block[1])
    for iter in itertools.permutations(changed_block_data):
        changed_block[0]._data = list(iter)
        if changed_block[0].recalculate_hash() == original_block_hash:
            print(f'The correct data was {iter}')
            break
