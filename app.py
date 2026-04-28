# ==============================================================================
# SEKME 3: İLERİ VERİ BİLİMİ VE İSTATİSTİK LABORATUVARI
# ==============================================================================
with tab_matematik:
    st.subheader("Veri Bilimi ve İstatistik Laboratuvarı")
    st.markdown("Sosyal medya şans değil, ileri matematiktir. Lütfen kullanmak istediğiniz matematiksel modeli seçin:")
    
    secilen_modul = st.selectbox("Analiz Modeli", [
        "1. Etkileşim (ER) ve Varyans İstikrar Analizi", 
        "2. İstatistiksel A/B Hipotez Testi (Z-Test)", 
        "3. İçerik Yarı Ömrü (Üstel Sönüm / Exponential Decay)",
        "4. Monte Carlo Simülasyonu (Olasılık ve Risk Analizi)",
        "5. İzlenme Dalgalanması ve Kırılma Noktası (Bollinger Bantları)" # YENİ EKLENDİ
    ])
    
    st.divider()

    # ... (Burada daha önceki 1, 2, 3 ve 4. modül kodları aynen kalacak) ...

    # ---------------------------------------------------------
    # MODÜL 5: İZLENME DALGALANMASI (YENİ)
    # ---------------------------------------------------------
    if "5." in secilen_modul:
        st.markdown("### 5. İzlenme Dalgalanması ve Kırılma Noktası (Bollinger Bantları)")
        st.caption("Son 10 videonuzun verisini girerek kanalınızın 'Dalgalanma Katsayısını (CV)' ve bir videonun viral veya çöküş sayılması için gereken sınır değerleri hesaplayın.")

        st.write("**Son 10 Videonuzun İzlenme Sayıları (Eskiden Yeniye):**")
        c1, c2, c3, c4, c5 = st.columns(5)
        d1 = c1.number_input("1. Video", value=1000, min_value=0)
        d2 = c2.number_input("2. Video", value=1200, min_value=0)
        d3 = c3.number_input("3. Video", value=950, min_value=0)
        d4 = c4.number_input("4. Video", value=1100, min_value=0)
        d5 = c5.number_input("5. Video", value=1050, min_value=0)
        
        c6, c7, c8, c9, c10 = st.columns(5)
        d6 = c6.number_input("6. Video", value=1300, min_value=0)
        d7 = c7.number_input("7. Video", value=1150, min_value=0)
        d8 = c8.number_input("8. Video", value=900, min_value=0)
        d9 = c9.number_input("9. Video", value=1400, min_value=0)
        d10 = c10.number_input("10. Video (En Yeni)", value=1250, min_value=0)

        if st.button("Dalgalanma ve Kırılma Analizi Yap", type="primary"):
            veri_seti = [d1, d2, d3, d4, d5, d6, d7, d8, d9, d10]
            ortalama = np.mean(veri_seti)
            standart_sapma = np.std(veri_seti)
            
            # Dalgalanma Katsayısı (Coefficient of Variation) = (Standart Sapma / Ortalama) * 100
            cv = (standart_sapma / ortalama) * 100 if ortalama > 0 else 0
            
            # Bollinger Bantları Mantığı (Ortalama +- 2 Standart Sapma)
            ust_bant = ortalama + (2 * standart_sapma)
            alt_bant = ortalama - (2 * standart_sapma)
            if alt_bant < 0: alt_bant = 0

            st.subheader("Matematiksel Kanal Profili")
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Ortalama İzlenme (μ)", f"{int(ortalama):,}")
            col_m2.metric("Dalgalanma Katsayısı (CV)", f"% {cv:.1f}")
            col_m3.metric("Standart Sapma (σ)", f"{int(standart_sapma):,}")

            st.subheader("Viral ve Çöküş (Flop) Sınırları")
            st.info(f"🚀 **Viral Kırılma Noktası (Üst Bant): {int(ust_bant):,}**\n\nBir videonuzun algoritma tarafından 'Viral' olarak algılanıp ekstra öne çıkarılması için izlenmesinin matematiksel olarak bu rakamı geçmesi gerekir.")
            st.error(f"📉 **Çöküş/Gölge Ban Sınırı (Alt Bant): {int(alt_bant):,}**\n\nBir videonuz bu rakamın altında kalıyorsa, algoritma sizi cezalandırıyor veya izleyici kancanız (hook) tamamen başarısız olmuş demektir.")

            # Şık bir grafik çizimi
            df_dalga = pd.DataFrame({
                "Videolar": [f"V{i}" for i in range(1, 11)],
                "İzlenme": veri_seti,
                "Ortalama": [ortalama] * 10,
                "Viral Sınırı": [ust_bant] * 10,
                "Çöküş Sınırı": [alt_bant] * 10
            })
            
            st.line_chart(df_dalga.set_index("Videolar"))

            if cv < 15:
                st.success("Analiz: Kanalınız İNANILMAZ İSTİKRARLI. İzleyicileriniz çok sadık. Büyük sıçramalar yapmıyorsunuz ama algoritmanın en sevdiği 'güvenilir üretici' profilisiniz.")
            elif cv < 40:
                st.warning("Analiz: Kanalınızda NORMAL DALGALANMA var. Sağlıklı bir profil. Yeni konseptler deneyerek üst bandı kırmaya çalışabilirsiniz.")
            else:
                st.error("Analiz: Kanalınızda AŞIRI DALGALANMA var. Algoritma kanalınızın tam olarak kime hitap ettiğini çözememiş. Belirli bir nişe (sektöre) odaklanmalısınız.")