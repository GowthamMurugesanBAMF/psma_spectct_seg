from ml_annotate_client import MLAnnotateClient
from collections import Counter
from pprint import pprint
from pathlib import Path
from tqdm.auto import tqdm
import requests

token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6InEtMjNmYWxldlpoaEQzaG05Q1Fia1A1TVF5VSJ9.eyJhdWQiOiJjNmY5NDUwYi02YjJjLTQ0NjYtYWI5Mi02ZDc4Y2QyODk2MTYiLCJpc3MiOiJodHRwczovL2xvZ2luLm1pY3Jvc29mdG9ubGluZS5jb20vNGRhYTViYjUtZjZkNC00M2M1LWI3MjQtYTJkYWM5M2IxYTMxL3YyLjAiLCJpYXQiOjE3MTM5NzY3MzUsIm5iZiI6MTcxMzk3NjczNSwiZXhwIjoxNzE0MDYzMzc1LCJhaW8iOiJBV1FBbS84V0FBQUFrcmczbVZLQUlaeERKdERpUngxY1pvdU1DTEVrTmJ5L0k1eVVuS09BcEF1R0oxM2xiQXhCOUh6am9Ia0xGd2Q5cnZKRkpWL2I5QkdwTzhjeXpBQVdSZE1BNEdyRWRxcUhrK1ltU0EvZUFEM3U0VktUQWVWcytBQm85a2w5STBWUyIsImVtYWlsIjoiZ293dGhhbS5tdXJ1Z2VzYW5AYmFtZmhlYWx0aC5jb20iLCJuYW1lIjoiR293dGhhbSBNdXJ1Z2VzYW4iLCJub25jZSI6Ijg4YzRiNDhjYTYyYzI2MjZhZTAyNDYzZDdhMmMxYzNiMzRjYjZiZWE2Zjc4NWY3MTUxYTJiOWIzYTQwZmRjNjEiLCJvaWQiOiJkZTdhN2ZmMC1mNDMwLTQ4ZDktODUwZi1hZGY1Yjk2OTIzNzkiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJnb3d0aGFtLm11cnVnZXNhbkBiYW1maGVhbHRoLmNvbSIsInJoIjoiMC5BU2tBdFZ1cVRkVDJ4VU8zSktMYXlUc2FNUXRGLWNZc2EyWkVxNUp0ZU0wb2xoWXBBSzAuIiwic3ViIjoiLTdLemVHZTBlUlVHVzBnZVdIb1hTNUZKa1pMM21Ba2RGcGZ1VkVuejZrWSIsInRpZCI6IjRkYWE1YmI1LWY2ZDQtNDNjNS1iNzI0LWEyZGFjOTNiMWEzMSIsInV0aSI6IlYxNFpUNU5Za2t5OF9pc3U2RXRSQVEiLCJ2ZXIiOiIyLjAifQ.qAkuCEz677prvMqI78ZfwK4z5QlRMHr32Z4Y7d0o6J1S_t1CTFaOsxSMFjbynVWEV4_TrVgGnt-FcnF9ROeQhT3im4tPsG4PlTMDPiJAV_mGO1F24UvwNVBpuxyXbAWfqcrTA_cj4ftaPS-dtTUTF-c6EumhDZVgHDHX7_Falya0eLKBaWhxYZcDJSsWf9l-CCgyqG8v2MRZLm7g_2HxB66ksGbTe6PUE7U3WsZJ_c4T2B4rKOUE3VUJZATjKvjzuf4g6Jo4YMZmFKathyVNUo8v9S_QJBltAqXbbZmcLegMJj7AG53uE9KdkNMTaZH3aIk-5Sg0T0LKpLT8cbbNCg"  # token from https://annotate.bamfhealth.com/

client = MLAnnotateClient(token)


# all spect tumor annotations were done under ticket task "psma_spect_tumors"

annotation_name = "psma_spect_tumors"

tks = client.tickets(annotation_name=annotation_name)


# number of tickets for each status

pprint(Counter([tk.status for tk in tks]))


# additional ticket filtering

tks = [
    tk for tk in tks if tk.status == "completed"
]  # only completed tickets, could have added this in the client.tickets call

tks = {tuple(tk.volume_ref): tk for tk in tks}  # only keep one ticket per volume_ref

# optional: could do additional filtering to pick the best ticket for each volume_ref


dataset_ticket_refs = [tk.ticket_ref for tk in tks.values()]
dest_dir = Path("spect_ct_data")
dest_dir.mkdir(parents=True, exist_ok=True)
for tk in tks.values():
    volume_ref = tk.volume_ref
    # print("volume_ref", volume_ref)
    op_path = dest_dir / volume_ref[0]
    op_path.mkdir(parents=True, exist_ok=True)
    tk.download_volume(op_path)  # downloading volumes works fine
    # downloading lables
    # issue only showing tickets with submitted or corrected status
    related_vols = tk.get_download_label_urls()
    for each_vol, info in related_vols.items():
        # print(each_vol, info)
        url = info["url"]
        resp = requests.get(url)
        resp.raise_for_status()
        status = info["status"]
        print(f"***{status}***")
        # if status == "completed":
        #     filename = op_path / f"{each_vol}_{status}.nrrd"
        #     with open(filename, "wb") as fp:
        #         fp.write(resp.content)
