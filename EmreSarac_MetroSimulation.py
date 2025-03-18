"""
Author: Emre
Date: 2025-03-17
Description: This project is a metro network simulation developed as a final project for the Global AI Hub - Akbank Python for AI 
Introduction Bootcamp. It calculates the fastest and least transfer routes using BFS and A algorithms.
"""
import heapq
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict, deque
from typing import Dict, List, Set, Tuple, Optional

class Istasyon:
    def __init__(self, idx: str, ad: str, hat: str):
        self.idx = idx
        self.ad = ad
        self.hat = hat
        self.komsular: List[Tuple['Istasyon', int]] = []  # (istasyon, süre) tuple'lari

    def komsu_ekle(self, istasyon: 'Istasyon', sure: int):
        self.komsular.append((istasyon, sure))
        
class MetroAgi:
    def __init__(self):
        self.istasyonlar: Dict[str, Istasyon] = {}
        self.hatlar: Dict[str, List[Istasyon]] = defaultdict(list)

    def istasyon_ekle(self, idx: str, ad: str, hat: str) -> None:
        if id not in self.istasyonlar:
            istasyon = Istasyon(idx, ad, hat)
            self.istasyonlar[idx] = istasyon
            self.hatlar[hat].append(istasyon)

    def baglanti_ekle(self, istasyon1_id: str, istasyon2_id: str, sure: int) -> None:
        istasyon1 = self.istasyonlar[istasyon1_id]
        istasyon2 = self.istasyonlar[istasyon2_id]
        istasyon1.komsu_ekle(istasyon2, sure)
        istasyon2.komsu_ekle(istasyon1, sure)
    
    def en_az_aktarma_bul(self, baslangic_id: str, hedef_id: str) -> Optional[List[Istasyon]]:
        """
        BFS algoritmasi kullanarak en az aktarmali rotayi bulur.

        Args:
            baslangic_id (str): Başlangiç istasyonunun benzersiz tanimlayicisi.
            hedef_id (str): Hedef istasyonunun benzersiz tanimlayicisi.

        Returns:
            Optional[List[Istasyon]]: Eğer rota bulunursa, başlangiçtan hedefe olan en az aktarmali rotayi 
                                  (Istasyon listesini) döndürür; rota bulunamazsa None döndürür.
        """       
        if baslangic_id not in self.istasyonlar or hedef_id not in self.istasyonlar:
            return None
        baslangic = self.istasyonlar[baslangic_id]
        hedef = self.istasyonlar[hedef_id]
        ziyaret_edildi = {baslangic}
        kuyruk = deque([(baslangic, [baslangic])])
        
        while kuyruk:
            
            istasyon, rota= kuyruk.popleft()
            if istasyon.idx == hedef.idx:
                return rota

            for komsu_istasyon, _ in istasyon.komsular:
                if komsu_istasyon not in ziyaret_edildi:
                    ziyaret_edildi.add(komsu_istasyon)
                    kuyruk.append((komsu_istasyon, rota + [komsu_istasyon]))
        return None

    def en_hizli_rota_bul(self, baslangic_id: str, hedef_id: str) -> Optional[Tuple[List[Istasyon], int]]:
        """
        A* algoritmasi kullanarak en hizli rotayi bulur.

        Args:
            baslangic_id (str): Başlangiç istasyonunun benzersiz tanimlayicisi.
            hedef_id (str): Hedef istasyonunun benzersiz tanimlayicisi.

        Returns:
            Optional[Tuple[List[Istasyon], int]]: Eğer rota bulunursa, başlangiçtan hedefe olan en hizli rotayi 
                                              (Istasyon listesini) ve toplam süreyi içeren bir tuple döndürür; 
                                              rota bulunamazsa None döndürür.
        """
        if baslangic_id not in self.istasyonlar or hedef_id not in self.istasyonlar:
            return None

        baslangic = self.istasyonlar[baslangic_id]
        hedef = self.istasyonlar[hedef_id]
        ziyaret_edildi = set()
        pq = [(0, id(baslangic), baslangic, [baslangic])] #(süre, id, istasyon, rota)
        
        while pq:

            sure, idx, istasyon, rota = heapq.heappop(pq)
            if istasyon.idx == hedef.idx:
                return rota + [istasyon], sure

            if istasyon in ziyaret_edildi:
                continue

            ziyaret_edildi.add(istasyon)

            for komsu_istasyon, komsu_gecis_sure in istasyon.komsular:
                toplam_sure = sure + komsu_gecis_sure
                heapq.heappush(pq, (toplam_sure, id(komsu_istasyon), komsu_istasyon, rota + [istasyon]))

        return None

            
    def goruntule(self, istasyon_bilgileri: bool):
        for hat, istasyonlar in self.hatlar.items():
            print(f"Hat: {hat}")
            if istasyon_bilgileri:
                for istasyon in istasyonlar:
                    print(f"  - {istasyon.ad} ({istasyon.idx})")
            print()

    def graf_ciz(self):
        G = nx.Graph()

        hat_renkleri = {
            "Kirmizi Hat": "red",
            "Mavi Hat": "blue",
            "Turuncu Hat": "orange"
        }

        # Ortak istasyonlari belirleme
        for istasyon in self.istasyonlar.values():
            if istasyon.ad not in G:
                G.add_node(istasyon.ad, label=istasyon.ad, hat=istasyon.hat)

        tum_sureler = [sure for istasyon in self.istasyonlar.values() for _, sure in istasyon.komsular]
        min_sure, max_sure = min(tum_sureler), max(tum_sureler)

        # Bağlantilari ekleme
        for istasyon in self.istasyonlar.values():
            for komsu, sure in istasyon.komsular:
                if istasyon.hat == komsu.hat:
                    weight = 1 + (9 - (sure - min_sure) / (max_sure - min_sure) * 8) #Ağirlik normalizasyonu
                    G.add_edge(istasyon.ad, komsu.ad, weight=weight, original_sure=sure, color=hat_renkleri[istasyon.hat])

        # Grafik çizim ayarlari
        pos = nx.spring_layout(G, seed=22, k=0.32, iterations=100)
        edge_colors = [G[u][v]["color"] for u, v in G.edges]

        # Çizim
        plt.figure(figsize=(10, 5))

        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=5)
        nx.draw_networkx_nodes(G, pos, node_size=100, node_color="white", alpha=1, linewidths=2, edgecolors="black")

        edge_labels = {(u, v): f"{G[u][v]['original_sure']} dk" for u, v in G.edges}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, font_color="black", bbox=dict(facecolor="white", edgecolor="none", alpha=0.7))

        # Pozisyonlari biraz yukariya taşimak için pos koordinatlarini değiştirelim
        labels = nx.get_node_attributes(G, "label")
        adjusted_pos = {node: (x - 0.02, y + 0.05) for node, (x, y) in pos.items()}
        for node, label in labels.items():
            x, y = adjusted_pos[node]
            plt.text(x, y, label, fontsize=10, fontweight="bold", rotation=-80, horizontalalignment="center", verticalalignment="bottom")

        # Başlik ve gösterim
        plt.title("Ankara Metro Hatti Haritasi", fontsize=12)
        plt.axis("off")  # Eksenleri kapatma
        plt.show()
        
# Örnek Kullanim
if __name__ == "__main__":
    metro = MetroAgi()
    
    # İstasyonlar ekleme
    # Kirmizi Hat
    metro.istasyon_ekle("K1", "Kizilay", "Kirmizi Hat")
    metro.istasyon_ekle("K2", "Ulus", "Kirmizi Hat")
    metro.istasyon_ekle("K3", "Demetevler", "Kirmizi Hat")
    metro.istasyon_ekle("K4", "OSB", "Kirmizi Hat")
    
    # Mavi Hat
    metro.istasyon_ekle("M1", "AŞTİ", "Mavi Hat")
    metro.istasyon_ekle("M2", "Kizilay", "Mavi Hat")  # Aktarma noktasi
    metro.istasyon_ekle("M3", "Sihhiye", "Mavi Hat")
    metro.istasyon_ekle("M4", "Gar", "Mavi Hat")
    
    # Turuncu Hat
    metro.istasyon_ekle("T1", "Batikent", "Turuncu Hat")
    metro.istasyon_ekle("T2", "Demetevler", "Turuncu Hat")  # Aktarma noktasi
    metro.istasyon_ekle("T3", "Gar", "Turuncu Hat")  # Aktarma noktasi
    metro.istasyon_ekle("T4", "Keçiören", "Turuncu Hat")
    
    # Bağlantilar ekleme
    # Kirmizi Hat bağlantilari
    metro.baglanti_ekle("K1", "K2", 4)  # Kizilay -> Ulus
    metro.baglanti_ekle("K2", "K3", 6)  # Ulus -> Demetevler
    metro.baglanti_ekle("K3", "K4", 8)  # Demetevler -> OSB
    
    # Mavi Hat bağlantilari
    metro.baglanti_ekle("M1", "M2", 5)  # AŞTİ -> Kizilay
    metro.baglanti_ekle("M2", "M3", 3)  # Kizilay -> Sihhiye
    metro.baglanti_ekle("M3", "M4", 4)  # Sihhiye -> Gar
    
    # Turuncu Hat bağlantilari
    metro.baglanti_ekle("T1", "T2", 7)  # Batikent -> Demetevler
    metro.baglanti_ekle("T2", "T3", 9)  # Demetevler -> Gar
    metro.baglanti_ekle("T3", "T4", 5)  # Gar -> Keçiören
    
    # Hat aktarma bağlantilari (ayni istasyon farkli hatlar)
    metro.baglanti_ekle("K1", "M2", 2)  # Kizilay aktarma
    metro.baglanti_ekle("K3", "T2", 3)  # Demetevler aktarma
    metro.baglanti_ekle("M4", "T3", 2)  # Gar aktarma

    # Metro graf
    metro.graf_ciz()
    
    # Test senaryolari
    print("\n=== Test Senaryolari ===")
    
    # Senaryo 1: AŞTİ'den OSB'ye
    print("\n1. AŞTİ'den OSB'ye:")
    rota = metro.en_az_aktarma_bul("M1", "K4")
    if rota:
        print("En az aktarmali rota:", " -> ".join(i.ad for i in rota))
    
    sonuc = metro.en_hizli_rota_bul("M1", "K4")
    if sonuc:
        rota, sure = sonuc
        print(f"En hizli rota ({sure} dakika):", " -> ".join(i.ad for i in rota))
    
    # Senaryo 2: Batikent'ten Keçiören'e
    print("\n2. Batikent'ten Keçiören'e:")
    rota = metro.en_az_aktarma_bul("T1", "T4")
    if rota:
        print("En az aktarmali rota:", " -> ".join(i.ad for i in rota))
    
    sonuc = metro.en_hizli_rota_bul("T1", "T4")
    if sonuc:
        rota, sure = sonuc
        print(f"En hizli rota ({sure} dakika):", " -> ".join(i.ad for i in rota))
    
    # Senaryo 3: Keçiören'den AŞTİ'ye
    print("\n3. Keçiören'den AŞTİ'ye:")
    rota = metro.en_az_aktarma_bul("T4", "M1")
    if rota:
        print("En az aktarmali rota:", " -> ".join(i.ad for i in rota))
    
    sonuc = metro.en_hizli_rota_bul("T4", "M1")
    if sonuc:
        rota, sure = sonuc
        print(f"En hizli rota ({sure} dakika):", " -> ".join(i.ad for i in rota)) 