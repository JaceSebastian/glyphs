import unittest
import necklaces

class Test_necklaces(unittest.TestCase):
    def test_cycle(self):
        og_list = [0,0,1,0]
        one_list = necklaces.cycle_list(og_list)
        neg_list = necklaces.cycle_list(og_list,-1)
        two_list = necklaces.cycle_list(og_list,2)
        
        self.assertEqual(one_list, [0,1,0,0])
        self.assertEqual(neg_list, [0,0,0,1])
        self.assertEqual(two_list,[1,0,0,0])
    def test_old_method(self):
        self.assertEqual(necklaces.generate_binary_strings(1),
                         ["0","1"])
        self.assertEqual(necklaces.generate_unique_combinations(1),[[0],[1]])

    def test_new_method(self):
        self.assertEqual(necklaces.tau_fn([0]),[1])
        self.assertEqual(necklaces.tau_fn([0,0]),[0,1])
        self.assertEqual(necklaces.tau_fn([1,1]),[1,0])

        test_output = [[0,1],[0,0]]
        self.assertEqual(necklaces.check_necklace(test_output,[0,1]),False)
        self.assertEqual(necklaces.check_necklace(test_output,[1,0]),False)
        self.assertEqual(necklaces.check_necklace([[0,0]],[1,0]),True)

        #running a few samples of the fast ones, if these are good I presume the high ones are too
        self.assertEqual(necklaces.generate_unique_combinations(3),
                        necklaces.generate_unique_binaries_ernesti(3))
        self.assertEqual(necklaces.generate_unique_combinations(4),
                         necklaces.generate_unique_binaries_ernesti(4))
        self.assertEqual(necklaces.generate_unique_combinations(5),
                         necklaces.generate_unique_binaries_ernesti(5))
        self.assertEqual(necklaces.generate_unique_combinations(6),
                         necklaces.generate_unique_binaries_ernesti(6))
if __name__ == "__main__":
    unittest.main()