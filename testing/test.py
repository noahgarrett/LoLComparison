import supabase
import bs4
import requests


def champ_names(client: supabase.Client):
    champs = client.table('champions').select("id", "name", "position").execute()
    print(champs.data)


def single_name(client: supabase.Client):
    champs = client.table('champions').select("name").eq("name", "Tahm Kench").execute()
    print(champs.data[0]['name'].lower().replace(' ', '').replace("'", "").replace(".", ""))


def soup_test():
    req = requests.get("https://na.op.gg/champions/darius/top/build?region=na&tier=platinum_plus")
    soup = bs4.BeautifulSoup(req.text, 'lxml')
    print(soup.findAll('div'))


def op_gg_api():
    response = requests.get('https://na.op.gg/api/rankings/champions/morgana?region=na&limit=5')
    print(response.content)
