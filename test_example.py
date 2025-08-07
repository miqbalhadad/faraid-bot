import unittest
from fractions import Fraction
from forward import ForwardChaining
from dempster import DempsterShafer

class TestForwardChaining(unittest.TestCase):
    """
    Test cases untuk metode Forward Chaining
    """
    
    def setUp(self):
        """Setup test environment"""
        self.fc = ForwardChaining()
    
    def test_basic_children_inheritance(self):
        """
        Test kasus dasar: anak laki-laki dan perempuan
        Berdasarkan QS. An-Nisa: 11
        """
        heirs_data = {
            'anak_laki': 1,
            'anak_perempuan': 1
        }
        
        result = self.fc.calculate_inheritance(heirs_data)
        
        # Pastikan ada hasil
        self.assertIn('shares', result)
        self.assertTrue(len(result['shares']) > 0)
        
        # Cek apakah anak laki-laki mendapat lebih banyak dari perempuan
        male_share = None
        female_share = None
        
        for heir, share in result['shares'].items():
            if 'Laki-laki' in heir:
                male_share = share['fraction']
            elif 'Perempuan' in heir:
                female_share = share['fraction']
        
        if male_share and female_share:
            # Anak laki-laki harus mendapat 2x anak perempuan
            self.assertAlmostEqual(float(male_share), float(female_share) * 2, places=3)
    
    def test_husband_with_children(self):
        """
        Test suami dengan anak: harus mendapat 1/4
        Berdasarkan QS. An-Nisa: 12
        """
        heirs_data = {
            'suami': 1,
            'anak_laki': 1
        }
        
        result = self.fc.calculate_inheritance(heirs_data)
        
        # Cari bagian suami
        husband_share = None
        for heir, share in result['shares'].items():
            if 'Suami' in heir:
                husband_share = share['fraction']
                break
        
        self.assertEqual(husband_share, Fraction(1, 4))
    
    def test_husband_without_children(self):
        """
        Test suami tanpa anak: harus mendapat 1/2
        """
        heirs_data = {
            'suami': 1,
            'ibu': 1
        }
        
        result = self.fc.calculate_inheritance(heirs_data)
        
        husband_share = None
        for heir, share in result['shares'].items():
            if 'Suami' in heir:
                husband_share = share['fraction']
                break
        
        self.assertEqual(husband_share, Fraction(1, 2))
    
    def test_validation_errors(self):
        """
        Test validasi input yang salah
        """
        # Test suami dan istri bersamaan
        invalid_data = {
            'suami': 1,
            'istri': 1
        }
        
        errors = self.fc.validate_heirs_data(invalid_data)
        self.assertTrue(len(errors) > 0)
        self.assertTrue(any('suami dan istri' in error.lower() for error in errors))
    
    def test_only_female_children(self):
        """
        Test hanya anak perempuan
        1 anak = 1/2, 2+ anak = 2/3 total
        """
        # Test 1 anak perempuan
        heirs_data_one = {'anak_perempuan': 1}
        result_one = self.fc.calculate_inheritance(heirs_data_one)
        
        female_share_one = None
        for heir, share in result_one['shares'].items():
            if 'Perempuan' in heir:
                female_share_one = share['fraction']
                break
        
        self.assertEqual(female_share_one, Fraction(1, 2))
        
        # Test 2 anak perempuan
        heirs_data_two = {'anak_perempuan': 2}
        result_two = self.fc.calculate_inheritance(heirs_data_two)
        
        total_female_share = Fraction(0)
        for heir, share in result_two['shares'].items():
            if 'Perempuan' in heir:
                total_female_share += share['fraction']
        
        self.assertEqual(total_female_share, Fraction(2, 3))

class TestDempsterShafer(unittest.TestCase):
    """
    Test cases untuk metode Dempster-Shafer Theory
    """
    
    def setUp(self):
        """Setup test environment"""
        self.ds = DempsterShafer()
    
    def test_frame_initialization(self):
        """
        Test inisialisasi frame of discernment
        """
        heirs_data = {
            'anak_laki': 1,
            'istri': 1,
            'ayah': 1
        }
        
        self.ds._initialize_frame_of_discernment(heirs_data)
        
        expected_heirs = {'Anak Laki-laki', 'Istri', 'Ayah'}
        self.assertEqual(self.ds.frame_of_discernment, expected_heirs)
    
    def test_evidence_creation(self):
        """
        Test pembuatan evidence sources
        """
        heirs_data = {
            'anak_laki': 1,
            'anak_perempuan': 1
        }
        
        self.ds._initialize_frame_of_discernment(heirs_data)
        evidence_sources = self.ds._create_evidence_sources(heirs_data)
        
        # Harus ada minimal satu evidence source
        self.assertTrue(len(evidence_sources) > 0)
        
        # Evidence pertama harus tentang keberadaan anak
        self.assertIn('Anak', evidence_sources[0]['name'])
    
    def test_mass_function_combination(self):
        """
        Test kombinasi mass functions menggunakan Dempster's rule
        """
        # Mass function 1
        mass1 = {
            frozenset(['A']): 0.6,
            frozenset(['A', 'B']): 0.4
        }
        
        # Mass function 2
        mass2 = {
            frozenset(['A']): 0.3,
            frozenset(['B']): 0.7
        }
        
        combined = self.ds._combine_mass_functions(mass1, mass2)
        
        # Hasil kombinasi harus valid (total mass = 1)
        total_mass = sum(combined.values())
        self.assertAlmostEqual(total_mass, 1.0, places=3)
    
    def test_full_calculation(self):
        """
        Test perhitungan lengkap Dempster-Shafer
        """
        heirs_data = {
            'anak_laki': 1,
            'istri': 1
        }
        
        result = self.ds.calculate_inheritance(heirs_data)
        
        # Pastikan ada hasil
        self.assertIn('shares', result)
        self.assertIn('total_certainty', result)
        self.assertIn('evidence_used', result)
        
        # Total certainty harus antara 0 dan 1
        self.assertGreaterEqual(result['total_certainty'], 0)
        self.assertLessEqual(result['total_certainty'], 1)
    
    def test_belief_calculation(self):
        """
        Test perhitungan belief values
        """
        # Setup simple case
        self.ds.frame_of_discernment = {'A', 'B'}
        self.ds.combined_mass = {
            frozenset(['A']): 0.4,
            frozenset(['B']): 0.3,
            frozenset(['A', 'B']): 0.3
        }
        
        self.ds._calculate_belief_and_plausibility()
        
        # Belief untuk A harus 0.4 (exact evidence)
        self.assertEqual(self.ds.belief_values['A'], 0.4)
        
        # Plausibility untuk A harus 0.4 + 0.3 = 0.7
        self.assertEqual(self.ds.plausibility_values['A'], 0.7)

class TestComparison(unittest.TestCase):
    """
    Test perbandingan antara Forward Chaining dan Dempster-Shafer
    """
    
    def setUp(self):
        """Setup test environment"""
        self.fc = ForwardChaining()
        self.ds = DempsterShafer()
    
    def test_same_input_both_methods(self):
        """
        Test input yang sama pada kedua metode
        """
        heirs_data = {
            'anak_laki': 1,
            'anak_perempuan': 1,
            'ibu': 1
        }
        
        fc_result = self.fc.calculate_inheritance(heirs_data)
        ds_result = self.ds.calculate_inheritance(heirs_data)
        
        # Kedua metode harus menghasilkan output
        self.assertTrue(len(fc_result['shares']) > 0)
        self.assertTrue(len(ds_result['shares']) > 0)
        
        # Kedua metode harus mengidentifikasi ahli waris yang sama
        fc_heirs = set(fc_result['shares'].keys())
        ds_heirs = set(ds_result['shares'].keys())
        
        # Minimal ada intersection dalam ahli waris yang diidentifikasi
        self.assertTrue(len(fc_heirs.intersection(ds_heirs)) > 0)
    
    def test_consistency_check(self):
        """
        Test konsistensi hasil antara metode
        """
        test_cases = [
            {'suami': 1, 'anak_laki': 1},
            {'istri': 1, 'anak_perempuan': 2},
            {'ayah': 1, 'ibu': 1, 'anak_laki': 1}
        ]
        
        for heirs_data in test_cases:
            fc_result = self.fc.calculate_inheritance(heirs_data)
            ds_result = self.ds.calculate_inheritance(heirs_data)
            
            # Tidak boleh ada error
            self.assertIsNotNone(fc_result)
            self.assertIsNotNone(ds_result)
            
            # Total distribusi tidak boleh lebih dari 100%
            fc_total = sum(share['percentage'] for share in fc_result['shares'].values())
            ds_total = sum(share['percentage'] for share in ds_result['shares'].values())
            
            self.assertLessEqual(fc_total, 100.01)  # Small tolerance for floating point
            self.assertLessEqual(ds_total, 100.01)

def run_sample_calculations():
    """
    Fungsi untuk menjalankan contoh perhitungan
    """
    print("🧪 CONTOH PERHITUNGAN WARISAN ISLAM")
    print("=" * 50)
    
    # Test case 1: Keluarga dengan anak laki-laki dan perempuan
    print("\n📋 Test Case 1: Anak laki-laki dan perempuan + Ibu")
    heirs_data_1 = {
        'anak_laki': 1,
        'anak_perempuan': 1,
        'ibu': 1
    }
    
    fc = ForwardChaining()
    ds = DempsterShafer()
    
    fc_result_1 = fc.calculate_inheritance(heirs_data_1)
    ds_result_1 = ds.calculate_inheritance(heirs_data_1)
    
    print("\n🔗 Forward Chaining:")
    for heir, share in fc_result_1['shares'].items():
        print(f"   {heir}: {share['fraction']} = {share['percentage']:.2f}%")
    
    print("\n🎯 Dempster-Shafer:")
    for heir, share in ds_result_1['shares'].items():
        belief = share.get('belief', 0)
        print(f"   {heir}: {share['fraction']} = {share['percentage']:.2f}% (Belief: {belief:.3f})")
    
    # Test case 2: Suami tanpa anak
    print("\n📋 Test Case 2: Suami + Ayah + Ibu (tanpa anak)")
    heirs_data_2 = {
        'suami': 1,
        'ayah': 1,
        'ibu': 1
    }
    
    fc_result_2 = fc.calculate_inheritance(heirs_data_2)
    ds_result_2 = ds.calculate_inheritance(heirs_data_2)
    
    print("\n🔗 Forward Chaining:")
    for heir, share in fc_result_2['shares'].items():
        print(f"   {heir}: {share['fraction']} = {share['percentage']:.2f}%")
    
    print("\n🎯 Dempster-Shafer:")
    for heir, share in ds_result_2['shares'].items():
        belief = share.get('belief', 0)
        print(f"   {heir}: {share['fraction']} = {share['percentage']:.2f}% (Belief: {belief:.3f})")
    
    print("\n✅ Contoh perhitungan selesai!")

if __name__ == '__main__':
    # Jalankan test cases
    print("🔬 MENJALANKAN TEST CASES")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Jalankan contoh perhitungan
    run_sample_calculations()