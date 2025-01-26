import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import re
from botasaurus.browser import browser, Driver


########## SCRAP INICIAL LIGA

@browser
def scrapper_liga( driver: Driver, data: dict):

    
    url_liga = "https://fbref.com/en/comps/12/stats/La-Liga-Stats"
    print("Iniciando o scrapper...")
    response = driver.get(url_liga)
    html = response.get_content()
    soup = BeautifulSoup(html, "html.parser")

        # Procure pela tabela
    table = soup.find("table", attrs={"id": "stats_standard"})

    # Verifique se a tabela foi encontrada
    if table:
        df = pd.read_html(str(table))[0]
        print("Tabela encontrada!")
        print(df.head())
    else:
        print("Tabela não encontrada!")

    df.columns = ['_'.join(col).strip() for col in df.columns.values]

    ## Tratando a tabela

    novo_df = df[['Unnamed: 1_level_0_Player', "Unnamed: 3_level_0_Pos",
        "Unnamed: 4_level_0_Squad", "Unnamed: 5_level_0_Age",
        "Playing Time_Min", "Performance_Gls", "Performance_Ast",
        'Performance_G+A', 'Performance_G-PK', 'Performance_PK', 'Performance_PKatt',
        'Performance_CrdY', 'Performance_CrdR', 'Expected_xG', 'Expected_npxG',
        'Expected_xAG', 'Expected_npxG+xAG', 'Progression_PrgC', 'Progression_PrgP',
        'Progression_PrgR']]

    # Renomeando as colunas para nomes mais legíveis
    novo_df.columns = ['Nome', 'Posição', 'Time', 'Idade',
                    'Minutos Jogados', 'Gols', 'Assistências', 'Gols + Assistências',
                    'Gols sem pênaltis', 'Pênaltis', 'Pênaltis tentados',
                    'Cartões Amarelos', 'Cartões Vermelhos', 'xG', 'npxG',
                    'xG esperado', 'npxG esperado', 'Progressão de Carregamento',
                    'Progressão de Passe', 'Progressão de Drible']

    novo_df = novo_df[novo_df['Time'] != 'Squad']

    ## Tratando idade

    novo_df['Idade'] = novo_df['Idade'].str.split('-').str[0]

    ## Tirando NaN

    novo_df = novo_df.dropna()

    ## Converter idade em número
    # Converter várias colunas para o tipo int em uma única linha
    novo_df = novo_df.astype({'Idade': 'int', 
                'Minutos Jogados': 'int',
                'Gols': 'int', 
                'Assistências': 'int',
                'Gols + Assistências': 'int',
                'Gols sem pênaltis': 'int',
                'Pênaltis': 'int',
                'Pênaltis tentados': 'int',
                'Cartões Amarelos': 'int',
                'Cartões Vermelhos': 'int',
                'xG': 'float',
                'npxG': 'float',
                'xG esperado': 'float',
                'npxG esperado': 'float',
                'Progressão de Carregamento': 'int',
                'Progressão de Passe': 'int',
                'Progressão de Drible': 'int'})



    player_cells = soup.find_all("td", attrs={"data-stat": "player"})
    players = []
    print("Criando dicionário com os jogadores...")
    for cell in player_cells:
        link = cell.find("a")
        if link:
            #print(link)
            #print(link.text)
            #print("https://fbref.com/" + link.get("href"))
            id = link.get("href").split("/")[3]
            #print(id)
            #Nome do jogador com hífens no lugar de espaço
            player = link.text.replace(" ", "-")
            players.append({
                "name": link.text,
                "profile_link": "https://fbref.com/" + link.get("href"),
                "id": id,
                "scouting_report": f"https://fbref.com/en/players/{id}/scout/12538/{player}-Scouting-Report"
            })


    ids = [player["id"] for player in players]
    df_id = pd.DataFrame(ids, columns=["id"])
    novo_df["ID"] = df_id

    print("Dicionário com os jogadores criado com sucesso.")
    df_dict =  novo_df.to_dict(orient='records')
    return players, df_dict



#### RUN

def main():
    players, df = scrapper_liga()
    df_pandas = pd.DataFrame(df)
    ## Salvar em CSV
    df_pandas.to_csv("data/liga.csv", index=False, encoding="utf-8")
    print(df_pandas.head())
    



if __name__ == "__main__":
    main()