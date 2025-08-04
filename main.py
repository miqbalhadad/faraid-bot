import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import asyncio
from forward import ForwardChaining
from dempster import DempsterShafer

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

ASKING_HEIRS, INPUT_DETAILS, CHOOSING_METHOD = range(3)

class WarisanBot:
    def __init__(self):
        """
        Inisialisasi bot dengan komponen Forward Chaining dan Dempster-Shafer
        """
        self.forward_chaining = ForwardChaining()
        self.dempster_shafer = DempsterShafer()
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler untuk command /start
        Memulai percakapan dan menjelaskan fungsi bot
        """
        welcome_message = """
🕌 **Assalamu'alaikum!**

Selamat datang di Bot Perhitungan Warisan Islam (Faraid) 📊

Bot ini akan membantu Anda menghitung pembagian warisan berdasarkan hukum Islam menggunakan dua metode:
1. **Forward Chaining** - Sistem berbasis aturan IF-THEN
2. **Dempster-Shafer Theory** - Sistem berbasis tingkat kepercayaan

Untuk memulai perhitungan, ketik /hitung

📚 Bot ini dibuat untuk keperluan penelitian skripsi
        """
        
        await update.message.reply_text(welcome_message)
        
    async def start_calculation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Memulai proses perhitungan warisan
        Inisialisasi data dan mulai menanyakan ahli waris
        """
        # Reset data sebelumnya
        context.user_data.clear()
        context.user_data['heirs'] = {}
        
        # Keyboard untuk memilih ahli waris
        keyboard = [
            ['Anak Laki-laki', 'Anak Perempuan'],
            ['Istri', 'Suami'],
            ['Ayah', 'Ibu'],
            ['Saudara Laki-laki', 'Saudara Perempuan'],
            ['Selesai Input']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
        
        await update.message.reply_text(
            "Mari kita mulai mendata ahli waris 📝\n\n"
            "Silakan pilih ahli waris yang ada, atau ketik 'Selesai Input' jika sudah selesai:",
            reply_markup=reply_markup
        )
        
        return ASKING_HEIRS
    
    async def process_heir_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Memproses input ahli waris dari user
        Menanyakan jumlah untuk setiap jenis ahli waris
        """
        user_input = update.message.text
        
        if user_input == 'Selesai Input':
            if not context.user_data['heirs']:
                await update.message.reply_text(
                    "Anda belum memasukkan ahli waris apapun. Silakan pilih minimal satu ahli waris."
                )
                return ASKING_HEIRS
            else:
                return await self.show_calculation_methods(update, context)
        
        # Mapping input ke kode internal
        heir_mapping = {
            'Anak Laki-laki': 'anak_laki',
            'Anak Perempuan': 'anak_perempuan', 
            'Istri': 'istri',
            'Suami': 'suami',
            'Ayah': 'ayah',
            'Ibu': 'ibu',
            'Saudara Laki-laki': 'saudara_laki',
            'Saudara Perempuan': 'saudara_perempuan'
        }
        
        if user_input in heir_mapping:
            context.user_data['current_heir'] = heir_mapping[user_input]
            context.user_data['current_heir_name'] = user_input
            
            await update.message.reply_text(
                f"Berapa jumlah {user_input}? (masukkan angka)",
                reply_markup=ReplyKeyboardRemove()
            )
            return INPUT_DETAILS
        else:
            await update.message.reply_text(
                "Pilihan tidak valid. Silakan pilih dari keyboard yang tersedia."
            )
            return ASKING_HEIRS
    
    async def process_heir_count(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Memproses jumlah ahli waris yang diinput user
        """
        try:
            count = int(update.message.text)
            if count <= 0:
                await update.message.reply_text(
                    "Jumlah harus lebih dari 0. Silakan masukkan ulang:"
                )
                return INPUT_DETAILS
                
            # Simpan data ahli waris
            heir_code = context.user_data['current_heir']
            context.user_data['heirs'][heir_code] = count
            
            # Keyboard untuk melanjutkan
            keyboard = [
                ['Anak Laki-laki', 'Anak Perempuan'],
                ['Istri', 'Suami'],
                ['Ayah', 'Ibu'],
                ['Saudara Laki-laki', 'Saudara Perempuan'],
                ['Selesai Input']
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
            
            await update.message.reply_text(
                f"✅ {context.user_data['current_heir_name']}: {count} orang telah dicatat\n\n"
                "Pilih ahli waris lainnya atau 'Selesai Input':",
                reply_markup=reply_markup
            )
            
            return ASKING_HEIRS
            
        except ValueError:
            await update.message.reply_text(
                "Input tidak valid. Silakan masukkan angka:"
            )
            return INPUT_DETAILS
    
    async def show_calculation_methods(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Menampilkan pilihan metode perhitungan
        """
        # Tampilkan ringkasan ahli waris
        summary = "📋 **Ringkasan Ahli Waris:**\n"
        heir_names = {
            'anak_laki': 'Anak Laki-laki',
            'anak_perempuan': 'Anak Perempuan',
            'istri': 'Istri',
            'suami': 'Suami',
            'ayah': 'Ayah',
            'ibu': 'Ibu',
            'saudara_laki': 'Saudara Laki-laki',
            'saudara_perempuan': 'Saudara Perempuan'
        }
        
        for heir_code, count in context.user_data['heirs'].items():
            summary += f"• {heir_names[heir_code]}: {count} orang\n"
        
        keyboard = [
            ['Forward Chaining'],
            ['Dempster-Shafer'],
            ['Bandingkan Kedua Metode'],
            ['Input Ulang']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            f"{summary}\n"
            "Pilih metode perhitungan:",
            reply_markup=reply_markup
        )
        
        return CHOOSING_METHOD
    
    async def calculate_inheritance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Melakukan perhitungan warisan berdasarkan metode yang dipilih
        """
        method = update.message.text
        heirs_data = context.user_data['heirs']
        
        if method == 'Forward Chaining':
            result = await self.calculate_forward_chaining(heirs_data)
            await update.message.reply_text(result, reply_markup=ReplyKeyboardRemove())
            
        elif method == 'Dempster-Shafer':
            result = await self.calculate_dempster_shafer(heirs_data)
            await update.message.reply_text(result, reply_markup=ReplyKeyboardRemove())
            
        elif method == 'Bandingkan Kedua Metode':
            fc_result = await self.calculate_forward_chaining(heirs_data)
            ds_result = await self.calculate_dempster_shafer(heirs_data)
            
            comparison = f"""
🔍 **PERBANDINGAN METODE PERHITUNGAN**

{fc_result}

{'='*50}

{ds_result}

📊 **Analisis Perbandingan:**
• Forward Chaining menggunakan aturan pasti berdasarkan Al-Quran dan Hadits
• Dempster-Shafer mempertimbangkan tingkat kepercayaan dan ketidakpastian
• Perbedaan hasil dapat terjadi karena pendekatan yang berbeda dalam menangani kasus kompleks
            """
            
            await update.message.reply_text(comparison, reply_markup=ReplyKeyboardRemove())
            
        elif method == 'Input Ulang':
            return await self.start_calculation(update, context)
        
        # Selesai, kembali ke menu utama
        await update.message.reply_text(
            "\n✅ Perhitungan selesai!\n\n"
            "Ketik /hitung untuk perhitungan baru\n"
            "Ketik /help untuk bantuan"
        )
        
        return ConversationHandler.END
    
    async def calculate_forward_chaining(self, heirs_data):
        """
        Melakukan perhitungan menggunakan Forward Chaining
        """
        try:
            result = self.forward_chaining.calculate_inheritance(heirs_data)
            
            output = "🔗 **METODE FORWARD CHAINING**\n\n"
            output += "📜 **Aturan yang Diterapkan:**\n"
            
            for rule in result['applied_rules']:
                output += f"• {rule}\n"
            
            output += "\n💰 **Hasil Pembagian:**\n"
            for heir, share in result['shares'].items():
                output += f"• {heir}: {share['fraction']} = {share['percentage']:.2f}%\n"
            
            if result['remaining'] > 0:
                output += f"\n⚠️ Sisa harta: {result['remaining']:.4f} (untuk distribusi 'asabah)\n"
                
            return output
            
        except Exception as e:
            return f"❌ Error dalam perhitungan Forward Chaining: {str(e)}"
    
    async def calculate_dempster_shafer(self, heirs_data):
        """
        Melakukan perhitungan menggunakan Dempster-Shafer Theory
        """
        try:
            result = self.dempster_shafer.calculate_inheritance(heirs_data)
            
            output = "🎯 **METODE DEMPSTER-SHAFER THEORY**\n\n"
            output += "📊 **Evidence dan Belief Functions:**\n"
            
            for evidence in result['evidence_used']:
                output += f"• {evidence}\n"
            
            output += "\n💰 **Hasil Pembagian:**\n"
            for heir, share in result['shares'].items():
                belief = share.get('belief', 0)
                output += f"• {heir}: {share['fraction']} = {share['percentage']:.2f}% (Belief: {belief:.3f})\n"
            
            output += f"\n🎲 **Tingkat Kepastian Total:** {result['total_certainty']:.3f}\n"
                
            return output
            
        except Exception as e:
            return f"❌ Error dalam perhitungan Dempster-Shafer: {str(e)}"
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler untuk command /help
        """
        help_text = """
🆘 **BANTUAN BOT WARISAN ISLAM**

**Perintah Utama:**
• /start - Memulai bot
• /hitung - Mulai perhitungan warisan
• /help - Menampilkan bantuan

**Cara Penggunaan:**
1. Ketik /hitung untuk memulai
2. Pilih jenis ahli waris yang ada
3. Masukkan jumlah masing-masing ahli waris
4. Pilih metode perhitungan
5. Lihat hasil pembagian

**Metode Perhitungan:**
• **Forward Chaining:** Menggunakan aturan IF-THEN berdasarkan Al-Quran dan Hadits
• **Dempster-Shafer:** Menggunakan tingkat kepercayaan dan menangani ketidakpastian

**Catatan:**
Bot ini adalah untuk keperluan penelitian dan edukasi. Untuk kasus kompleks, konsultasikan dengan ahli hukum Islam.
        """
        
        await update.message.reply_text(help_text)
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler untuk membatalkan percakapan
        """
        await update.message.reply_text(
            "Perhitungan dibatalkan. Ketik /hitung untuk memulai lagi.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

def main():
    """
    Fungsi utama untuk menjalankan bot
    """
    # Masukkan token bot Telegram Anda di sini
    TOKEN = "8167947644:AAFAsi1EK2sjmQT8SaIZ7veDkkmltq2LmoQ"  # Ganti dengan token bot Anda
    
    # Inisialisasi bot
    warisan_bot = WarisanBot()
    
    # Buat aplikasi
    application = Application.builder().token(TOKEN).build()
    
    # Setup conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('hitung', warisan_bot.start_calculation)],
        states={
            ASKING_HEIRS: [MessageHandler(filters.TEXT & ~filters.COMMAND, warisan_bot.process_heir_input)],
            INPUT_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, warisan_bot.process_heir_count)],
            CHOOSING_METHOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, warisan_bot.calculate_inheritance)],
        },
        fallbacks=[CommandHandler('cancel', warisan_bot.cancel)],
    )
    
    # Tambahkan handlers
    application.add_handler(CommandHandler("start", warisan_bot.start))
    application.add_handler(CommandHandler("help", warisan_bot.help_command))
    application.add_handler(conv_handler)
    
    # Jalankan bot
    print("🤖 Bot Warisan Islam telah aktif!")
    print("Tekan Ctrl+C untuk menghentikan bot")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()