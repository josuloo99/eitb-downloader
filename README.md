# EITB Downloader

Script honek EITBko plataforma digitaletatik (Primeran, Makusi eta ETBOn) bideoak deskargatzeko eta desenkriptatzeko aukera ematen du. Horretarako, plataformek eskaitzen duten APIa baliatzen da.

## Dependentziak

Hasteko, bi binario deskargatu behar dira, eta nahi den karpetan egotzi (errazena proiektu honen erroan egoztea da).
- [N_m3u8DL-RE](https://github.com/nilaoda/N_m3u8DL-RE/releases). Honek m3u8 fitxategia oinarritzat hartuta bideo eta audio enkriptatua deskargatzen du zerbitzarietatik zuzenean.
- [mp4decrypt](https://www.bento4.com/downloads/). MP4 bideo fitxategiak maneiatzeko toolkit bat da. Baina guri _mp4decrypt_ bakarrik interesatzen zaigu (`/bin` karpeta barruan aurkitzen da), enkriptatutako bideoa desenkriptatzeko. Informazio gehiagorako dokumentazioa [hemen](https://www.bento4.com/documentation/mp4decrypt/) aurkitu daiteke.

Bestalde, Python dependentzia pakete batzuk ere behar dira, _requirements.txt_ fitxategian definituta daudenak.

## Dependentzien instalazioa, konfigurazioa eta erabilera.

_eitb_downloader_ erabiltzeko pausuak hauek dira:
1. `N_m3u8DL-RE` eta `mp4decrypt` binarioak deskargatu, erauzi eta proiektu honen erroan kopiatu.
2. `config.py` fitxategi bat sortu erroan, `config.py.template` fitxategitik abiatuta. Bertan, bi binario hauen kokalekuak definitu behar dira:

```python
M3U_DOWNLOADER_PATH = "./N_m3u8DL-RE"
MP4DECRYPTER_PATH = "./mp4decrypt"
DECRYPT_KEY = "<desekriptatzeko-kodea>"
```

3. Python ingurune birtual bat sortu eta aktibatu, python dependentziak ondo kudeatzeko.

```python
python3 -m venv .venv
source .venv/bin/activate
```

5. Dependentziak instalatu

```python
pip install -r requirements.txt
```

4. Script nagusia martxan jarri.

```python
python main.py
```
