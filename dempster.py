"""
Dempster-Shafer Theory Implementation untuk Perhitungan Warisan Islam
Menggunakan belief functions dan evidence combination untuk menangani ketidakpastian

Author: [Your Name]
Referensi: Dempster-Shafer Theory of Evidence, Glenn Shafer (1976)
Aplikasi: Sistem Warisan Islam dengan tingkat kepercayaan
"""

from fractions import Fraction
import itertools
from collections import defaultdict
import math

class DempsterShafer:
    def __init__(self):
        """
        Inisialisasi sistem Dempster-Shafer untuk perhitungan warisan
        """
        self.frame_of_discernment = set()  # Θ (Theta) - set semua kemungkinan ahli waris
        self.mass_functions = []  # Daftar basic probability assignments
        self.evidence_sources = []  # Sumber-sumber evidence
        self.combined_mass = {}  # Hasil kombinasi mass functions
        self.belief_values = {}  # Nilai belief untuk setiap hipotesis
        self.plausibility_values = {}  # Nilai plausibility
        
    def _initialize_frame_of_discernment(self, heirs_data):
        """
        Menginisialisasi frame of discernment berdasarkan ahli waris yang ada
        
        Args:
            heirs_data (dict): Data ahli waris
        """
        self.frame_of_discernment = set()
        
        # Tambahkan setiap jenis ahli waris ke frame
        for heir_type, count in heirs_data.items():
            if count > 0:
                heir_names = {
                    'anak_laki': 'Anak Laki-laki',
                    'anak_perempuan': 'Anak Perempuan',
                    'suami': 'Suami',
                    'istri': 'Istri',
                    'ayah': 'Ayah',
                    'ibu': 'Ibu',
                    'saudara_laki': 'Saudara Laki-laki',
                    'saudara_perempuan': 'Saudara Perempuan'
                }
                
                if heir_type in heir_names:
                    if count == 1:
                        self.frame_of_discernment.add(heir_names[heir_type])
                    else:
                        for i in range(count):
                            self.frame_of_discernment.add(f"{heir_names[heir_type]} {i+1}")
    
    def _create_evidence_sources(self, heirs_data):
        """
        Membuat sumber-sumber evidence berdasarkan aturan-aturan Faraid
        Setiap aturan menjadi sumber evidence dengan tingkat kepercayaan tertentu
        """
        evidence_sources = []
        
        # Evidence 1: Keberadaan anak (kepercayaan tinggi = 0.95)
        if heirs_data.get('anak_laki', 0) > 0 or heirs_data.get('anak_perempuan', 0) > 0:
            mass_func = {}
            
            # Anak laki-laki memiliki evidence kuat untuk mendapat bagian besar
            if heirs_data.get('anak_laki', 0) > 0:
                for i in range(heirs_data['anak_laki']):
                    heir_name = f"Anak Laki-laki {i+1}" if heirs_data['anak_laki'] > 1 else "Anak Laki-laki"
                    mass_func[frozenset([heir_name])] = 0.4 / heirs_data['anak_laki']
            
            # Anak perempuan memiliki evidence sedang
            if heirs_data.get('anak_perempuan', 0) > 0:
                for i in range(heirs_data['anak_perempuan']):
                    heir_name = f"Anak Perempuan {i+1}" if heirs_data['anak_perempuan'] > 1 else "Anak Perempuan"
                    mass_func[frozenset([heir_name])] = 0.2 / heirs_data['anak_perempuan']
            
            # Sisa mass untuk uncertainty
            total_assigned = sum(mass_func.values())
            if total_assigned < 1.0:
                mass_func[frozenset(self.frame_of_discernment)] = 1.0 - total_assigned
            
            evidence_sources.append({
                'name': 'Evidence Keberadaan Anak',
                'mass_function': mass_func,
                'reliability': 0.95
            })
        
        # Evidence 2: Status pernikahan (kepercayaan tinggi = 0.9)
        if heirs_data.get('suami', 0) > 0 or heirs_data.get('istri', 0) > 0:
            mass_func = {}
            
            if heirs_data.get('suami', 0) > 0:
                # Suami memiliki hak yang jelas dalam Al-Quran
                has_children = heirs_data.get('anak_laki', 0) > 0 or heirs_data.get('anak_perempuan', 0) > 0
                confidence = 0.7 if has_children else 0.8  # Lebih pasti jika tidak ada anak
                mass_func[frozenset(['Suami'])] = confidence
            
            if heirs_data.get('istri', 0) > 0:
                istri_count = heirs_data['istri']
                has_children = heirs_data.get('anak_laki', 0) > 0 or heirs_data.get('anak_perempuan', 0) > 0
                confidence = 0.6 if has_children else 0.7
                
                for i in range(istri_count):
                    heir_name = f"Istri {i+1}" if istri_count > 1 else "Istri"
                    mass_func[frozenset([heir_name])] = confidence / istri_count
            
            # Sisa untuk uncertainty
            total_assigned = sum(mass_func.values())
            if total_assigned < 1.0:
                mass_func[frozenset(self.frame_of_discernment)] = 1.0 - total_assigned
            
            evidence_sources.append({
                'name': 'Evidence Status Pernikahan',
                'mass_function': mass_func,
                'reliability': 0.9
            })
        
        # Evidence 3: Keberadaan orang tua (kepercayaan sedang = 0.8)
        if heirs_data.get('ayah', 0) > 0 or heirs_data.get('ibu', 0) > 0:
            mass_func = {}
            
            if heirs_data.get('ayah', 0) > 0:
                # Ayah bisa menjadi asabah
                has_male_children = heirs_data.get('anak_laki', 0) > 0
                confidence = 0.5 if has_male_children else 0.7
                mass_func[frozenset(['Ayah'])] = confidence
            
            if heirs_data.get('ibu', 0) > 0:
                # Ibu memiliki bagian yang relatif pasti
                has_children = heirs_data.get('anak_laki', 0) > 0 or heirs_data.get('anak_perempuan', 0) > 0
                many_siblings = (heirs_data.get('saudara_laki', 0) + heirs_data.get('saudara_perempuan', 0)) >= 2
                confidence = 0.6 if (has_children or many_siblings) else 0.7
                mass_func[frozenset(['Ibu'])] = confidence
            
            # Sisa untuk uncertainty
            total_assigned = sum(mass_func.values())
            if total_assigned < 1.0:
                mass_func[frozenset(self.frame_of_discernment)] = 1.0 - total_assigned
            
            evidence_sources.append({
                'name': 'Evidence Keberadaan Orang Tua',
                'mass_function': mass_func,
                'reliability': 0.8
            })
        
        # Evidence 4: Keberadaan saudara (kepercayaan rendah = 0.6)
        if heirs_data.get('saudara_laki', 0) > 0 or heirs_data.get('saudara_perempuan', 0) > 0:
            # Saudara hanya mendapat bagian jika tidak ada ayah dan anak laki-laki
            no_father = heirs_data.get('ayah', 0) == 0
            no_male_children = heirs_data.get('anak_laki', 0) == 0
            
            if no_father and no_male_children:
                mass_func = {}
                
                if heirs_data.get('saudara_laki', 0) > 0:
                    for i in range(heirs_data['saudara_laki']):
                        heir_name = f"Saudara Laki-laki {i+1}" if heirs_data['saudara_laki'] > 1 else "Saudara Laki-laki"
                        mass_func[frozenset([heir_name])] = 0.3 / heirs_data['saudara_laki']
                
                if heirs_data.get('saudara_perempuan', 0) > 0:
                    for i in range(heirs_data['saudara_perempuan']):
                        heir_name = f"Saudara Perempuan {i+1}" if heirs_data['saudara_perempuan'] > 1 else "Saudara Perempuan"
                        mass_func[frozenset([heir_name])] = 0.2 / heirs_data['saudara_perempuan']
                
                # Sisa untuk uncertainty
                total_assigned = sum(mass_func.values())
                if total_assigned < 1.0:
                    mass_func[frozenset(self.frame_of_discernment)] = 1.0 - total_assigned
                
                evidence_sources.append({
                    'name': 'Evidence Keberadaan Saudara',
                    'mass_function': mass_func,
                    'reliability': 0.6
                })
        
        return evidence_sources
    
    def _combine_mass_functions(self, mass1, mass2):
        """
        Mengkombinasikan dua mass functions menggunakan Dempster's rule of combination
        
        Args:
            mass1, mass2: Dictionary mass functions
            
        Returns:
            dict: Combined mass function
        """
        combined = defaultdict(float)
        conflict = 0.0
        
        # Hitung kombinasi untuk setiap pasangan focal elements
        for A, m1_A in mass1.items():
            for B, m2_B in mass2.items():
                intersection = A & B  # Irisan dari A dan B
                
                if intersection:
                    # Ada irisan - kontribusi ke combined mass
                    combined[intersection] += m1_A * m2_B
                else:
                    # Tidak ada irisan - kontribusi ke konflik
                    conflict += m1_A * m2_B
        
        # Normalisasi jika ada konflik
        if conflict < 1.0:
            normalization_factor = 1.0 / (1.0 - conflict)
            for focal_set in combined:
                combined[focal_set] *= normalization_factor
        else:
            # Konflik total - tidak dapat dikombinasikan
            return {}
        
        return dict(combined)
    
    def _calculate_belief_and_plausibility(self):
        """
        Menghitung nilai belief dan plausibility untuk setiap singleton
        """
        self.belief_values = {}
        self.plausibility_values = {}
        
        for element in self.frame_of_discernment:
            belief = 0.0
            plausibility = 0.0
            
            # Belief: jumlah mass dari semua subset yang mengandung element
            for focal_set, mass in self.combined_mass.items():
                if element in focal_set:
                    if len(focal_set) == 1:  # Exact evidence untuk element ini
                        belief += mass
                
                # Plausibility: jumlah mass dari semua set yang beririsan dengan {element}
                if element in focal_set:
                    plausibility += mass
            
            self.belief_values[element] = belief
            self.plausibility_values[element] = plausibility
    
    def _convert_to_inheritance_shares(self):
        """
        Mengkonversi belief values menjadi bagian warisan
        Menggunakan kombinasi belief dan aturan Faraid tradisional
        """
        shares = {}
        total_belief = sum(self.belief_values.values())
        
        if total_belief == 0:
            # Jika tidak ada belief yang definitif, gunakan plausibility
            total_belief = sum(self.plausibility_values.values())
            belief_source = self.plausibility_values
        else:
            belief_source = self.belief_values
        
        # Normalisasi dan konversi ke fraction
        for heir, belief in belief_source.items():
            if total_belief > 0:
                normalized_belief = belief / total_belief
                
                # Konversi ke fraction yang mendekati aturan Faraid
                fraction = self._approximate_faraid_fraction(heir, normalized_belief)
                
                shares[heir] = {
                    'fraction': fraction,
                    'percentage': float(fraction) * 100,
                    'belief': belief,
                    'plausibility': self.plausibility_values.get(heir, 0)
                }
        
        return shares
    
    def _approximate_faraid_fraction(self, heir_name, normalized_belief):
        """
        Mengonversi normalized belief menjadi fraction yang mendekati aturan Faraid
        """
        # Daftar fraction umum dalam Faraid
        common_fractions = [
            Fraction(1, 2), Fraction(1, 3), Fraction(1, 4), Fraction(1, 6), Fraction(1, 8),
            Fraction(2, 3), Fraction(3, 4), Fraction(5, 6), Fraction(7, 8),
            Fraction(1, 12), Fraction(5, 12), Fraction(7, 12)
        ]
        
        # Aturan khusus berdasarkan jenis ahli waris
        if 'Anak Laki-laki' in heir_name:
            # Anak laki-laki cenderung mendapat bagian besar
            if normalized_belief > 0.4:
                return Fraction(1, 2)
            elif normalized_belief > 0.2:
                return Fraction(1, 3)
            else:
                return Fraction(1, 4)
        
        elif 'Anak Perempuan' in heir_name:
            # Anak perempuan cenderung mendapat setengah dari anak laki-laki
            if normalized_belief > 0.3:
                return Fraction(1, 3)
            elif normalized_belief > 0.15:
                return Fraction(1, 4)
            else:
                return Fraction(1, 6)
        
        elif heir_name == 'Suami':
            # Suami: 1/4 jika ada anak, 1/2 jika tidak
            if normalized_belief > 0.4:
                return Fraction(1, 2)
            else:
                return Fraction(1, 4)
        
        elif 'Istri' in heir_name:
            # Istri: 1/8 jika ada anak, 1/4 jika tidak
            if normalized_belief > 0.2:
                return Fraction(1, 4)
            else:
                return Fraction(1, 8)
        
        elif heir_name == 'Ayah':
            # Ayah: 1/6 atau sisa sebagai asabah
            if normalized_belief > 0.3:
                return Fraction(1, 3)
            else:
                return Fraction(1, 6)
        
        elif heir_name == 'Ibu':
            # Ibu: 1/6 atau 1/3
            if normalized_belief > 0.25:
                return Fraction(1, 3)
            else:
                return Fraction(1, 6)
        
        # Default: cari fraction terdekat
        target_value = normalized_belief
        closest_fraction = min(common_fractions, 
                             key=lambda f: abs(float(f) - target_value))
        
        return closest_fraction
    
    def calculate_inheritance(self, heirs_data):
        """
        Fungsi utama untuk menghitung warisan menggunakan Dempster-Shafer Theory
        
        Args:
            heirs_data (dict): Data ahli waris
            
        Returns:
            dict: Hasil perhitungan dengan belief values dan bagian warisan
        """
        # Inisialisasi frame of discernment
        self._initialize_frame_of_discernment(heirs_data)
        
        # Buat sumber-sumber evidence
        self.evidence_sources = self._create_evidence_sources(heirs_data)
        
        if not self.evidence_sources:
            return {
                'shares': {},
                'evidence_used': ['Tidak ada evidence yang dapat digunakan'],
                'total_certainty': 0.0,
                'conflict_level': 0.0
            }
        
        # Kombinasikan mass functions
        self.combined_mass = self.evidence_sources[0]['mass_function'].copy()
        
        for i in range(1, len(self.evidence_sources)):
            self.combined_mass = self._combine_mass_functions(
                self.combined_mass, 
                self.evidence_sources[i]['mass_function']
            )
        
        # Hitung belief dan plausibility
        self._calculate_belief_and_plausibility()
        
        # Konversi ke bagian warisan
        shares = self._convert_to_inheritance_shares()
        
        # Hitung tingkat kepastian total
        total_certainty = sum(self.belief_values.values())
        
        # Evidence yang digunakan
        evidence_descriptions = [
            f"{source['name']} (Reliabilitas: {source['reliability']:.2f})"
            for source in self.evidence_sources
        ]
        
        return {
            'shares': shares,
            'evidence_used': evidence_descriptions,
            'total_certainty': total_certainty,
            'belief_values': self.belief_values,
            'plausibility_values': self.plausibility_values,
            'combined_mass': dict(self.combined_mass)
        }
    
    def get_detailed_analysis(self):
        """
        Memberikan analisis detail tentang proses Dempster-Shafer
        """
        analysis = "Analisis Detail Dempster-Shafer Theory:\n\n"
        
        analysis += "1. Frame of Discernment (Θ):\n"
        analysis += f"   {self.frame_of_discernment}\n\n"
        
        analysis += "2. Evidence Sources:\n"
        for i, source in enumerate(self.evidence_sources, 1):
            analysis += f"   {i}. {source['name']}\n"
            analysis += f"      Reliabilitas: {source['reliability']}\n"
            for focal_set, mass in source['mass_function'].items():
                analysis += f"      m({set(focal_set)}): {mass:.3f}\n"
            analysis += "\n"
        
        analysis += "3. Combined Mass Function:\n"
        for focal_set, mass in self.combined_mass.items():
            analysis += f"   m({set(focal_set)}): {mass:.3f}\n"
        
        analysis += "\n4. Belief dan Plausibility Values:\n"
        for element in self.frame_of_discernment:
            belief = self.belief_values.get(element, 0)
            plausibility = self.plausibility_values.get(element, 0)
            analysis += f"   {element}: Bel = {belief:.3f}, Pl = {plausibility:.3f}\n"
        
        return analysis