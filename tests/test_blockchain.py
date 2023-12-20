import unittest
from block import Block
from blockchain import Blockchain

class TestBlockchain(unittest.TestCase):

    def setUp(self):
        # Initialiser une instance de la classe Blockchain pour les tests
        self.blockchain = Blockchain()

    def test_add_block(self):
        # Vérifier si la méthode add_block ajoute correctement un bloc à la blockchain
        block_data = "Test Block Data"

        new_block = Block(1, "timestamp", block_data, "previous_hash")
        self.blockchain.add_block(new_block)
        self.assertEqual(len(self.blockchain.blocks), 2)  # La blockchain doit maintenant avoir deux blocs

    def test_get_last_block_index(self):
        # Vérifier si la méthode get_last_block_index renvoie l'index du dernier bloc correctement
        self.assertEqual(self.blockchain.get_last_block_index(), 0)  # La blockchain a un seul bloc après l'initialisation

        # Ajouter un autre bloc à la blockchain
        new_block = Block(1, "timestamp", "Data", "previous_hash")
        self.blockchain.add_block(new_block)

        self.assertEqual(self.blockchain.get_last_block_index(), 1)  # Maintenant, la blockchain doit avoir deux blocs, et l'index du dernier bloc doit être 1

if __name__ == '__main__':
    unittest.main()
