from fractions import Fraction

class ForwardChaining:
    def __init__(self):
        """
        Inisialisasi sistem Forward Chaining dengan aturan-aturan Faraid
        """
        self.rules = []
        self.applied_rules = []
        self.facts = {}
        self.shares = {}
        
        # Inisialisasi aturan-aturan warisan Islam
        self._initialize_rules()
    
    def _initialize_rules(self):
        """
        Mendefinisikan aturan-aturan warisan Islam dalam format IF-THEN
        Berdasarkan Al-Quran dan Hadits
        """
        
        # ATURAN UNTUK ANAK
        self.rules.append({
            'name': 'Anak Laki-laki dan Perempuan',
            'condition': lambda facts: facts.get('anak_laki', 0) > 0 and facts.get('anak_perempuan', 0) > 0,
            'action': self._rule_mixed_children,
            'description': 'Jika ada anak laki-laki dan perempuan: laki-laki = 2x perempuan'
        })
        
        self.rules.append({
            'name': 'Hanya Anak Laki-laki',
            'condition': lambda facts: facts.get('anak_laki', 0) > 0 and facts.get('anak_perempuan', 0) == 0,
            'action': self._rule_only_male_children,
            'description': 'Jika hanya ada anak laki-laki: mendapat seluruh sisa harta sebagai asabah'
        })
        
        self.rules.append({
            'name': 'Hanya Anak Perempuan',
            'condition': lambda facts: facts.get('anak_laki', 0) == 0 and facts.get('anak_perempuan', 0) > 0,
            'action': self._rule_only_female_children,
            'description': 'Jika hanya ada anak perempuan: 1 anak = 1/2, 2+ anak = 2/3'
        })
        
        # ATURAN UNTUK SUAMI/ISTRI
        self.rules.append({
            'name': 'Suami dengan Anak',
            'condition': lambda facts: facts.get('suami', 0) > 0 and (facts.get('anak_laki', 0) > 0 or facts.get('anak_perempuan', 0) > 0),
            'action': lambda: self._set_share('Suami', Fraction(1, 4)),
            'description': 'Suami mendapat 1/4 jika ada anak'
        })
        
        self.rules.append({
            'name': 'Suami tanpa Anak',
            'condition': lambda facts: facts.get('suami', 0) > 0 and facts.get('anak_laki', 0) == 0 and facts.get('anak_perempuan', 0) == 0,
            'action': lambda: self._set_share('Suami', Fraction(1, 2)),
            'description': 'Suami mendapat 1/2 jika tidak ada anak'
        })
        
        self.rules.append({
            'name': 'Istri dengan Anak',
            'condition': lambda facts: facts.get('istri', 0) > 0 and (facts.get('anak_laki', 0) > 0 or facts.get('anak_perempuan', 0) > 0),
            'action': lambda: self._distribute_wives_share(Fraction(1, 8)),
            'description': 'Istri mendapat 1/8 jika ada anak'
        })
        
        self.rules.append({
            'name': 'Istri tanpa Anak',
            'condition': lambda facts: facts.get('istri', 0) > 0 and facts.get('anak_laki', 0) == 0 and facts.get('anak_perempuan', 0) == 0,
            'action': lambda: self._distribute_wives_share(Fraction(1, 4)),
            'description': 'Istri mendapat 1/4 jika tidak ada anak'
        })
        
        # ATURAN UNTUK ORANG TUA
        self.rules.append({
            'name': 'Ayah dengan Anak',
            'condition': lambda facts: facts.get('ayah', 0) > 0 and (facts.get('anak_laki', 0) > 0 or facts.get('anak_perempuan', 0) > 0),
            'action': lambda: self._set_share('Ayah', Fraction(1, 6)),
            'description': 'Ayah mendapat 1/6 jika ada anak'
        })
        
        self.rules.append({
            'name': 'Ayah tanpa Anak Laki-laki',
            'condition': lambda facts: facts.get('ayah', 0) > 0 and facts.get('anak_laki', 0) == 0,
            'action': self._rule_father_without_male_child,
            'description': 'Ayah sebagai asabah jika tidak ada anak laki-laki'
        })
        
        self.rules.append({
            'name': 'Ibu dengan Anak atau Saudara',
            'condition': lambda facts: facts.get('ibu', 0) > 0 and (
                facts.get('anak_laki', 0) > 0 or facts.get('anak_perempuan', 0) > 0 or
                facts.get('saudara_laki', 0) >= 2 or facts.get('saudara_perempuan', 0) >= 2
            ),
            'action': lambda: self._set_share('Ibu', Fraction(1, 6)),
            'description': 'Ibu mendapat 1/6 jika ada anak atau 2+ saudara'
        })
        
        self.rules.append({
            'name': 'Ibu tanpa Anak dan Saudara Sedikit',
            'condition': lambda facts: facts.get('ibu', 0) > 0 and (
                facts.get('anak_laki', 0) == 0 and facts.get('anak_perempuan', 0) == 0 and
                facts.get('saudara_laki', 0) < 2 and facts.get('saudara_perempuan', 0) < 2
            ),
            'action': lambda: self._set_share('Ibu', Fraction(1, 3)),
            'description': 'Ibu mendapat 1/3 jika tidak ada anak dan saudara kurang dari 2'
        })
        
        # ATURAN UNTUK SAUDARA (disederhanakan)
        self.rules.append({
            'name': 'Saudara jika tidak ada Ayah dan Anak',
            'condition': lambda facts: (facts.get('saudara_laki', 0) > 0 or facts.get('saudara_perempuan', 0) > 0) and \
                                     facts.get('ayah', 0) == 0 and facts.get('anak_laki', 0) == 0,
            'action': self._rule_siblings,
            'description': 'Saudara mendapat bagian jika tidak ada ayah dan anak laki-laki'
        })
    
    def _set_share(self, heir_name, fraction):
        """
        Menetapkan bagian warisan untuk ahli waris tertentu
        """
        self.shares[heir_name] = {
            'fraction': fraction,
            'percentage': float(fraction) * 100
        }
    
    def _distribute_wives_share(self, total_fraction):
        """
        Membagi bagian istri jika lebih dari satu
        """
        wives_count = self.facts.get('istri', 1)
        individual_share = total_fraction / wives_count
        
        for i in range(wives_count):
            wife_name = f"Istri {i+1}" if wives_count > 1 else "Istri"
            self._set_share(wife_name, individual_share)
    
    def _rule_mixed_children(self):
        """
        Aturan untuk anak laki-laki dan perempuan bersama-sama
        Berdasarkan QS. An-Nisa: 11 - "lildzakari mitslu hazhzhi untsayain"
        """
        male_count = self.facts['anak_laki']
        female_count = self.facts['anak_perempuan']
        
        # Total bagian = 2x (jumlah laki-laki) + 1x (jumlah perempuan)
        total_parts = (2 * male_count) + female_count
        
        # Tentukan sisa harta setelah bagian pasti lainnya
        remaining_fraction = self._calculate_remaining_fraction()
        
        # Bagian per unit
        unit_share = remaining_fraction / total_parts
        
        # Anak laki-laki mendapat 2 unit, perempuan 1 unit
        male_share = unit_share * 2
        female_share = unit_share
        
        for i in range(male_count):
            name = f"Anak Laki-laki {i+1}" if male_count > 1 else "Anak Laki-laki"
            self._set_share(name, male_share)
            
        for i in range(female_count):
            name = f"Anak Perempuan {i+1}" if female_count > 1 else "Anak Perempuan"
            self._set_share(name, female_share)
    
    def _rule_only_male_children(self):
        """
        Aturan untuk hanya anak laki-laki (sebagai 'asabah)
        """
        male_count = self.facts['anak_laki']
        remaining_fraction = self._calculate_remaining_fraction()
        
        individual_share = remaining_fraction / male_count
        
        for i in range(male_count):
            name = f"Anak Laki-laki {i+1}" if male_count > 1 else "Anak Laki-laki"
            self._set_share(name, individual_share)
    
    def _rule_only_female_children(self):
        """
        Aturan untuk hanya anak perempuan
        Berdasarkan QS. An-Nisa: 11
        """
        female_count = self.facts['anak_perempuan']
        
        if female_count == 1:
            # Satu anak perempuan mendapat 1/2
            self._set_share("Anak Perempuan", Fraction(1, 2))
        else:
            # Dua atau lebih anak perempuan mendapat 2/3 dibagi rata
            total_share = Fraction(2, 3)
            individual_share = total_share / female_count
            
            for i in range(female_count):
                name = f"Anak Perempuan {i+1}"
                self._set_share(name, individual_share)
    
    def _rule_father_without_male_child(self):
        """
        Aturan untuk ayah ketika tidak ada anak laki-laki
        Ayah menjadi 'asabah dan mendapat sisa
        """
        if self.facts.get('anak_perempuan', 0) > 0:
            # Jika ada anak perempuan, ayah mendapat 1/6 + sisa
            self._set_share('Ayah', Fraction(1, 6))
            # Sisa akan dihitung sebagai 'asabah
        else:
            # Jika tidak ada anak sama sekali, ayah sebagai 'asabah penuh
            remaining = self._calculate_remaining_fraction()
            self._set_share('Ayah', remaining)
    
    def _rule_siblings(self):
        """
        Aturan untuk saudara (disederhanakan)
        Hanya berlaku jika tidak ada ayah dan anak laki-laki
        """
        male_siblings = self.facts.get('saudara_laki', 0)
        female_siblings = self.facts.get('saudara_perempuan', 0)
        
        remaining = self._calculate_remaining_fraction()
        
        if male_siblings > 0 and female_siblings > 0:
            # Saudara laki-laki dan perempuan: 2:1
            total_parts = (2 * male_siblings) + female_siblings
            unit_share = remaining / total_parts
            
            for i in range(male_siblings):
                name = f"Saudara Laki-laki {i+1}" if male_siblings > 1 else "Saudara Laki-laki"
                self._set_share(name, unit_share * 2)
                
            for i in range(female_siblings):
                name = f"Saudara Perempuan {i+1}" if female_siblings > 1 else "Saudara Perempuan"
                self._set_share(name, unit_share)
                
        elif male_siblings > 0:
            # Hanya saudara laki-laki
            individual_share = remaining / male_siblings
            for i in range(male_siblings):
                name = f"Saudara Laki-laki {i+1}" if male_siblings > 1 else "Saudara Laki-laki"
                self._set_share(name, individual_share)
                
        elif female_siblings == 1:
            # Satu saudara perempuan mendapat 1/2
            self._set_share("Saudara Perempuan", min(remaining, Fraction(1, 2)))
        elif female_siblings > 1:
            # Dua atau lebih saudara perempuan mendapat 2/3
            total_share = min(remaining, Fraction(2, 3))
            individual_share = total_share / female_siblings
            for i in range(female_siblings):
                name = f"Saudara Perempuan {i+1}"
                self._set_share(name, individual_share)
    
    def _calculate_remaining_fraction(self):
        """
        Menghitung sisa harta setelah bagian-bagian pasti (fara'id)
        """
        total_fixed_shares = Fraction(0, 1)
        
        for heir, share_info in self.shares.items():
            total_fixed_shares += share_info['fraction']
        
        remaining = Fraction(1, 1) - total_fixed_shares
        return max(remaining, Fraction(0, 1))  # Tidak boleh negatif
    
    def calculate_inheritance(self, heirs_data):
        """
        Fungsi utama untuk menghitung warisan menggunakan Forward Chaining
        
        Args:
            heirs_data (dict): Data ahli waris dalam format {'anak_laki': 2, 'istri': 1, ...}
            
        Returns:
            dict: Hasil perhitungan dengan aturan yang diterapkan dan bagian masing-masing
        """
        # Reset data sebelumnya
        self.facts = heirs_data.copy()
        self.shares = {}
        self.applied_rules = []
        
        # Terapkan aturan-aturan secara berurutan
        for rule in self.rules:
            if rule['condition'](self.facts):
                # Jalankan aksi aturan
                rule['action']()
                # Catat aturan yang diterapkan
                self.applied_rules.append(rule['description'])
        
        # Hitung sisa harta
        remaining = self._calculate_remaining_fraction()
        
        # Distribusi sisa kepada 'asabah jika ada
        if remaining > 0:
            self._distribute_remaining_to_asabah(remaining)
        
        # Normalisasi jika total > 1 (kasus 'awl)
        self._handle_awl_case()
        
        # Format hasil
        result = {
            'shares': self.shares,
            'applied_rules': self.applied_rules,
            'remaining': float(remaining),
            'total_distributed': sum(share['fraction'] for share in self.shares.values())
        }
        
        return result
    
    def _distribute_remaining_to_asabah(self, remaining):
        """
        Mendistribusikan sisa harta kepada ahli waris 'asabah
        """
        # Prioritas 'asabah: anak laki-laki, ayah, saudara laki-laki
        if self.facts.get('anak_laki', 0) > 0 and 'Anak Laki-laki' not in [k for k in self.shares.keys() if 'Anak Laki-laki' in k]:
            # Jika anak laki-laki belum mendapat bagian penuh
            male_count = self.facts['anak_laki']
            additional_share = remaining / male_count
            
            for i in range(male_count):
                name = f"Anak Laki-laki {i+1}" if male_count > 1 else "Anak Laki-laki"
                if name in self.shares:
                    self.shares[name]['fraction'] += additional_share
                    self.shares[name]['percentage'] = float(self.shares[name]['fraction']) * 100
        
        elif self.facts.get('ayah', 0) > 0 and remaining > 0:
            # Ayah sebagai 'asabah
            if 'Ayah' in self.shares:
                self.shares['Ayah']['fraction'] += remaining
                self.shares['Ayah']['percentage'] = float(self.shares['Ayah']['fraction']) * 100
            else:
                self._set_share('Ayah', remaining)
    
    def _handle_awl_case(self):
        """
        Menangani kasus 'Awl (ketika total bagian > 1)
        Mengurangi proporsional semua bagian
        """
        total_shares = sum(share['fraction'] for share in self.shares.values())
        
        if total_shares > 1:
            # Kasus 'Awl - kurangi semua bagian secara proporsional
            reduction_factor = Fraction(1, 1) / total_shares
            
            for heir in self.shares:
                original_fraction = self.shares[heir]['fraction']
                self.shares[heir]['fraction'] = original_fraction * reduction_factor
                self.shares[heir]['percentage'] = float(self.shares[heir]['fraction']) * 100
            
            self.applied_rules.append(f"Kasus 'Awl: Total bagian {total_shares} > 1, dilakukan pengurangan proporsional")
    
    def get_detailed_explanation(self):
        """
        Memberikan penjelasan detail tentang aturan yang diterapkan
        """
        explanation = "Penjelasan Detail Forward Chaining:\n\n"
        
        for i, rule in enumerate(self.applied_rules, 1):
            explanation += f"{i}. {rule}\n"
        
        explanation += f"\nTotal aturan yang diterapkan: {len(self.applied_rules)}"
        
        return explanation
    
    def validate_heirs_data(self, heirs_data):
        """
        Validasi data ahli waris untuk memastikan konsistensi
        """
        errors = []
        
        # Validasi dasar
        if not heirs_data:
            errors.append("Data ahli waris tidak boleh kosong")
            return errors
        
        # Tidak boleh ada suami dan istri bersamaan
        if heirs_data.get('suami', 0) > 0 and heirs_data.get('istri', 0) > 0:
            errors.append("Tidak boleh ada suami dan istri dalam satu kasus warisan")
        
        # Maksimal satu suami
        if heirs_data.get('suami', 0) > 1:
            errors.append("Suami hanya boleh satu orang")
        
        # Maksimal satu ayah dan satu ibu
        if heirs_data.get('ayah', 0) > 1:
            errors.append("Ayah hanya boleh satu orang")
        
        if heirs_data.get('ibu', 0) > 1:
            errors.append("Ibu hanya boleh satu orang")
        
        # Semua nilai harus positif
        for heir, count in heirs_data.items():
            if count < 0:
                errors.append(f"Jumlah {heir} tidak boleh negatif")
        
        return errors