"""These edge tests tackle type and value errors for most of the integer
and double fields - and the string size field which contains an integer -
for the Product_Information.xlsx file (our primary catalog file).
Approximately split between Type and ValueError, there are six tests
related to pricing, four related to size, and six related to reviews.

Edge test functions 1 through 16 do not have returns.

The load.py file can be used to load Product_Information.xlsx by calling upon
the run_edge_tests(PATH) function where PATH is the path to an xlsx file.
For use in project the run_edge_tests function returns a dataframe of product
information. However, for the edge tests we use an unassigned
function call."""

import unittest
from load import run_edge_tests


##########################################################
# Run Six Edge Tests on Pricing
##########################################################

print("Running Six Price Column Edge Tests")

class EdgeTest1(unittest.TestCase):
    """EdgeTest1 of 16."""
    def test_check_price_type_ounce(self):
        """Check that price_per_oz column not contains NaN or string."""
        with self.assertRaises(TypeError):
            PRODUCTS_PATH = "tests/data/price/Product_Information_Price_Ounce_String.xlsx"
            run_edge_tests(PRODUCTS_PATH)

suite = unittest.TestLoader().loadTestsFromTestCase(EdgeTest1)
_ = unittest.TextTestRunner().run(suite)


class EdgeTest2(unittest.TestCase):
    """EdgeTest2 of 16."""
    def test_check_price_type_numeric(self):
        """Check that price_numeric column not contains a NaN or string."""
        with self.assertRaises(TypeError):
            PRODUCTS_PATH = "tests/data/price/Product_Information_Price_Numeric_String.xlsx"
            run_edge_tests(PRODUCTS_PATH)

suite = unittest.TestLoader().loadTestsFromTestCase(EdgeTest2)
_ = unittest.TextTestRunner().run(suite)


class EdgeTest3(unittest.TestCase):
    """EdgeTest3 of 16."""
    def test_check_price_type(self):
        """Check that price column cannot have string."""
        with self.assertRaises(TypeError):
            PRODUCTS_PATH = "tests/data/price/Product_Information_Price_String.xlsx"
            run_edge_tests(PRODUCTS_PATH)

suite = unittest.TestLoader().loadTestsFromTestCase(EdgeTest3)
_ = unittest.TextTestRunner().run(suite)


class EdgeTest4(unittest.TestCase):
    """EdgeTest4 of 16."""
    def test_check_price_value_ounce(self):
        """Check price_per_oz 'column - and perhaps other price
        columns - cannot be 0 or less than 0."""
        with self.assertRaises(ValueError):
            PRODUCTS_PATH = "tests/data/price/Product_Information_Price_Ounce_Negative.xlsx"
            run_edge_tests(PRODUCTS_PATH)

suite = unittest.TestLoader().loadTestsFromTestCase(EdgeTest4)
_ = unittest.TextTestRunner().run(suite)


class EdgeTest5(unittest.TestCase):
    """EdgeTest5 of 16."""
    def test_check_price_value(self):
        """Check price 'column - and perhaps other price
        columns - cannot be 0 or less than 0."""
        with self.assertRaises(ValueError):
            PRODUCTS_PATH = "tests/data/price/Product_Information_Price_Negative.xlsx"
            run_edge_tests(PRODUCTS_PATH)

suite = unittest.TestLoader().loadTestsFromTestCase(EdgeTest5)
_ = unittest.TextTestRunner().run(suite)


class EdgeTest6(unittest.TestCase):
    """EdgeTest6 of 16."""
    def test_check_price_value_numeric(self):
        """Check price_numeric column - and perhaps other price
        columns - cannot be 0 or less than 0."""
        with self.assertRaises(ValueError):
            PRODUCTS_PATH = "tests/data/price/Product_Information_Price_Numeric.xlsx"
            run_edge_tests(PRODUCTS_PATH)

suite = unittest.TestLoader().loadTestsFromTestCase(EdgeTest6)
_ = unittest.TextTestRunner().run(suite)


##########################################################
# Run Four Edge Tests on Size
##########################################################

print("Running Four Size Column Edge Tests")

class EdgeTest7(unittest.TestCase):
    """EdgeTest7 of 16."""
    def test_check_size_type_numeric(self):
        """Check first size character is not an integer."""
        with self.assertRaises(TypeError):
            PRODUCTS_PATH = "tests/data/size/Product_Information_Size_String.xlsx"
            run_edge_tests(PRODUCTS_PATH)

suite = unittest.TestLoader().loadTestsFromTestCase(EdgeTest7)
_ = unittest.TextTestRunner().run(suite)


class EdgeTest8(unittest.TestCase):
    """EdgeTest8 of 16."""
    def test_check_size_type_ounce(self):
        """Check size_oz column cannot have string."""
        with self.assertRaises(TypeError):
            PRODUCTS_PATH = "tests/data/size/Product_Information_Size_Ounce_String.xlsx"
            run_edge_tests(PRODUCTS_PATH)

suite = unittest.TestLoader().loadTestsFromTestCase(EdgeTest8)
_ = unittest.TextTestRunner().run(suite)


class EdgeTest9(unittest.TestCase):
    """EdgeTest9 of 16."""
    def test_check_size_value_ounce(self):
        """Check size column cannot equal zero."""
        with self.assertRaises(ValueError):
            PRODUCTS_PATH = "tests/data/size/Product_Information_Size_Zero.xlsx"
            run_edge_tests(PRODUCTS_PATH)

suite = unittest.TestLoader().loadTestsFromTestCase(EdgeTest9)
_ = unittest.TextTestRunner().run(suite)


class EdgeTest10(unittest.TestCase):
    """EdgeTest10 of 16."""
    def test_check_size_value_ounce(self):
        """Check size_oz column cannot be less than or equal to zero."""
        with self.assertRaises(ValueError):
            PRODUCTS_PATH = "tests/data/size/Product_Information_Size_Ounce_Zero.xlsx"
            run_edge_tests(PRODUCTS_PATH)

suite = unittest.TestLoader().loadTestsFromTestCase(EdgeTest10)
_ = unittest.TextTestRunner().run(suite)

##########################################################
# Run Six Edge Tests on Reviews
##########################################################

print("Running Six Review Column Edge Tests")

class EdgeTest11(unittest.TestCase):
    """EdgeTest11 of 16."""
    def test_check_reviews_type_hearts(self):
        """Check hearts column cannot have string data"""
        with self.assertRaises(TypeError):
            PRODUCTS_PATH = "tests/data/reviews/Product_Information_Hearts_String.xlsx"
            run_edge_tests(PRODUCTS_PATH)

suite = unittest.TestLoader().loadTestsFromTestCase(EdgeTest11)
_ = unittest.TextTestRunner().run(suite)

class EdgeTest12(unittest.TestCase):
    """EdgeTest12 of 16."""
    def test_check_reviews_type_hearts_percentage(self):
        """Check heart_percentage column cannot have string."""
        with self.assertRaises(TypeError):
            PRODUCTS_PATH = "tests/data/reviews/Product_Information_Hearts_Percentage_String.xlsx"
            run_edge_tests(PRODUCTS_PATH)

suite = unittest.TestLoader().loadTestsFromTestCase(EdgeTest12)
_ = unittest.TextTestRunner().run(suite)

class EdgeTest13(unittest.TestCase):
    """EdgeTest13 of 16."""
    def test_check_reviews_type(self):
        """Check total_reviews column cannot have string."""
        with self.assertRaises(TypeError):
            PRODUCTS_PATH = "tests/data/reviews/Product_Information_Reviews_String.xlsx"
            run_edge_tests(PRODUCTS_PATH)

suite = unittest.TestLoader().loadTestsFromTestCase(EdgeTest13)
_ = unittest.TextTestRunner().run(suite)


class EdgeTest14(unittest.TestCase):
    """EdgeTest14 of 16."""
    def test_check_numeric_reviews(self):
        """Check total_reviews column cannot be 0 or less than 0."""
        with self.assertRaises(ValueError):
            PRODUCTS_PATH = "tests/data/reviews/Product_Information_Reviews_Zero.xlsx"
            run_edge_tests(PRODUCTS_PATH)

suite = unittest.TestLoader().loadTestsFromTestCase(EdgeTest14)
_ = unittest.TextTestRunner().run(suite)


class EdgeTest15(unittest.TestCase):
    """EdgeTest15 of 16."""
    def test_check_numeric_reviews_hearts_percentage(self):
        """Check heart_percentage column cannot be 0 or less than 0."""
        with self.assertRaises(ValueError):
            PRODUCTS_PATH = "tests/data/reviews/Product_Information_Hearts_Percentage_Zero.xlsx"
            run_edge_tests(PRODUCTS_PATH)

suite = unittest.TestLoader().loadTestsFromTestCase(EdgeTest15)
_ = unittest.TextTestRunner().run(suite)


class EdgeTest16(unittest.TestCase):
    """EdgeTest16 of 16."""
    def test_check_numeric_reviews_hearts(self):
        """Chech hearts column cannot be 0 or less than 0."""
        with self.assertRaises(ValueError):
            PRODUCTS_PATH = "tests/data/reviews/Product_Information_Hearts_Zero.xlsx"
            run_edge_tests(PRODUCTS_PATH)

suite = unittest.TestLoader().loadTestsFromTestCase(EdgeTest16)
_ = unittest.TextTestRunner().run(suite)




print('End of testing')

if __name__ == '__main__':
    unittest.main()
