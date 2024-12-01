import json
import random
import pandas as pd
import tabulate
from datetime import datetime, timedelta

### Global Variables ###########################################################
ANO = 2025
FERIADOS = {
    "feriados_nacionais": [
        { "data_inicio": "2025-01-01", "data_fim": "2025-01-01", "nome": "Confraternização Universal" },
        { "data_inicio": "2025-03-03", "data_fim": "2025-03-04", "nome": "Carnaval" },
        { "data_inicio": "2025-04-18", "data_fim": "2025-04-18", "nome": "Paixão de Cristo" },
        { "data_inicio": "2025-04-21", "data_fim": "2025-04-21", "nome": "Tiradentes" },
        { "data_inicio": "2025-05-01", "data_fim": "2025-05-01", "nome": "Dia do Trabalho" },
        { "data_inicio": "2025-06-19", "data_fim": "2025-06-19", "nome": "Corpus Christi" },
        # { "data_inicio": "2025-09-07", "data_fim": "2025-09-07", "nome": "Independência do Brasil" }, # Domingo
        # { "data_inicio": "2025-10-12", "data_fim": "2025-10-12", "nome": "Nossa Senhora Aparecida" }, # Domingo
        # { "data_inicio": "2025-11-02", "data_fim": "2025-11-02", "nome": "Finados" }, # Domingo
        # { "data_inicio": "2025-11-15", "data_fim": "2025-11-15", "nome": "Proclamação da República" }, # Sábado
        { "data_inicio": "2025-11-20", "data_fim": "2025-11-20", "nome": "Dia Nacional de Zumbi e da Consciência Negra" },
        { "data_inicio": "2025-12-25", "data_fim": "2025-12-25", "nome": "Natal" }
    ],
    "feriados_regionais": [
        { "data_inicio": "2025-01-20", "data_fim": "2025-01-20", "nome": "Dia de São Sebastião" },
        { "data_inicio": "2025-04-23", "data_fim": "2025-04-23", "nome": "Dia de São Jorge" }        
    ]
}
FAMILIAS = [
    "Maria", "Madalena", "Carlos", "Suely"
]

### Custom Exceptions #########################################################

class MissingBusinessRule(Exception):
    pass

### Functions #################################################################

def rand_familia(list_familias):
    if len(list_familias) == 1:
        return list_familias[0]
    else:
        return random.choice(list_familias)

def rand_feriados(list_feriados):
    if len(list_feriados) == 1:
        return list_feriados[0]
    else:
        return random.choice(list_feriados)

def get_fds_mais_proximo(feriado):
    dt_inicio = datetime.strptime(feriado["data_inicio"], "%Y-%m-%d")
    dt_fim = datetime.strptime(feriado["data_fim"], "%Y-%m-%d")

    dt_inicio_weekday = dt_inicio.weekday()
    dt_fim_weekday = dt_fim.weekday()

    # Segunda-feira = 0, Terça-feira = 1, ..., Domingo = 6
    #   Se o feriado começa entre sexta e segunda, o fim de semana é da data do sábado, entre esse range de dias
    if dt_inicio_weekday == 4:
        dt_fds = dt_inicio + timedelta(days=1)
    elif dt_inicio_weekday == 5:
        dt_fds = dt_inicio
    elif dt_inicio_weekday == 6:
        dt_fds = dt_inicio - timedelta(days=1)
    elif dt_inicio_weekday == 0:
        dt_fds = dt_inicio - timedelta(days=2)

    #   Se o feriado termina entre 6a e segunda, o fim de semana é da data do sábado, entre esse range de dias
    elif dt_fim_weekday == 4:
        dt_fds = dt_fim + timedelta(days=1)
    elif dt_fim_weekday == 5:
        dt_fds = dt_fim
    elif dt_fim_weekday == 6:
        dt_fds = dt_fim - timedelta(days=1)
    elif dt_fim_weekday == 0:
        dt_fds = dt_fim - timedelta(days=2)


    #   Se o feriado começa na terça calcula o sábado anterior e se começa na quinta calcula o sábado posterior
    elif dt_inicio_weekday == 1:
        dt_fds = dt_inicio - timedelta(days=3)
    elif dt_inicio_weekday == 3:
        dt_fds = dt_inicio + timedelta(days=2)

    #   Se o feriado termina na quinta calcula o sábado posterior e se termina na terça calcula o sábado anterior
    elif dt_fim_weekday == 3:
        dt_fds = dt_fim + timedelta(days=2)
    elif dt_fim_weekday == 1:
        dt_fds = dt_fim - timedelta(days=3)

    #   Se o feriado começa na quarta, considera o sábado posterior
    elif dt_inicio_weekday == 2:
        # dt_fds = random.choice([dt_inicio - timedelta(days=4), dt_inicio + timedelta(days=3)])
        dt_fds = dt_inicio + timedelta(days=3)

    #   Se o feriado termina na quarta, considera o sábado anterior
    elif dt_fim_weekday == 2:
        # dt_fds = random.choice([dt_fim - timedelta(days=4), dt_fim + timedelta(days=3)])
        dt_fds = dt_fim - timedelta(days=4)

    else:
        raise MissingBusinessRule(f"Regra de negócio não implementada para data de início {feriado['data_inicio']} no dia da semana {dt_inicio.strftime('%A')}, nem na data de fim {feriado['data_fim']} no dia da semana {dt_fim.strftime('%A')}")

    return dt_fds


### Main ######################################################################

def main():
    # list_feriados é uma lista que junta os feriados nacionais e regionais
    list_feriados = FERIADOS["feriados_nacionais"].copy()
    list_feriados.extend(FERIADOS["feriados_regionais"].copy())
    list_feriados = sorted(list_feriados, key=lambda x: x["data_inicio"])

    # list_familias é uma lista temporária pra armazenar as famílias que ainda não foram sorteadas
    list_familias = FAMILIAS.copy()

    # list_sorteio_fds é a lista que armazena os sorteios dos fins de semana
    list_sorteio_fds = []

    # Começamos o sorteio sorteando os feriados, e então associado às famílias, travando os finsd e semana
    last_familia = None
    for feriado in list_feriados:

        if len(list_familias) == 0:
            list_familias = FAMILIAS.copy()

        familia = rand_familia(list_familias)

        # Diminui a chance de sortear a mesma família em feriados consecutivos
        if last_familia == familia:
            familia = rand_familia(list_familias)
        else:
            last_familia = familia

        list_familias.remove(familia)

        day = get_fds_mais_proximo(feriado)

        list_sorteio_fds.append(
            {
                "feriado": True,
                "nome_feriado": feriado["nome"],
                "dia_da_semana_inicio": datetime.strptime(feriado["data_inicio"], "%Y-%m-%d").strftime("%A"),
                "dia_da_semana_fim": datetime.strptime(feriado["data_fim"], "%Y-%m-%d").strftime("%A"),
                "familia": familia,
                "fim_de_semana": datetime.strftime(day, "%Y-%m-%d"),
                "semana_ano": datetime.strftime(day, "%W")
            }
        )

    sorted_list = sorted(list_sorteio_fds, key=lambda x: x["semana_ano"])
    df = pd.DataFrame(sorted_list)

    print("Feriados sorteados:")
    print(tabulate.tabulate(df, headers='keys', tablefmt='psql'))

    print("\nTotais:")
    df_summary = df.groupby(["familia"]).size().reset_index(name="qtd_feriados")
    print(tabulate.tabulate(df_summary, headers='keys', tablefmt='psql'))
    print("\n")

    last_familia = None
    list_familias = FAMILIAS.copy()

    # Percorremos todos os dias do ano ignorando os que não são sábado, e ignorando os que já foram sorteados, e sorteamos as famílias
    day = datetime.strptime(f"{ANO}-01-01", "%Y-%m-%d")
    while day <= datetime.strptime(f"{ANO}-12-31", "%Y-%m-%d"):
        if day.weekday() != 5:
            day += timedelta(days=1)
            continue

        if len(list_familias) == 0:
            list_familias = FAMILIAS.copy()

        familia = rand_familia(list_familias)
        # Diminui a chance de sortear a mesma família em fins de semana consecutivos
        if last_familia == familia:
            familia = rand_familia(list_familias)
        else:
            last_familia = familia

        if any([x["fim_de_semana"] == datetime.strftime(day, "%Y-%m-%d") for x in list_sorteio_fds]):
            feriado_sorteado = [x for x in list_sorteio_fds if x["fim_de_semana"] == datetime.strftime(day, "%Y-%m-%d")][0]
            last_familia = feriado_sorteado["familia"]
            day += timedelta(days=1)
            continue

        list_familias.remove(familia)

        list_sorteio_fds.append(
            {
                "feriado": False,
                "nome_feriado": None,
                "dia_da_semana_inicio": None,
                "dia_da_semana_fim": None,
                "familia": familia,
                "fim_de_semana": datetime.strftime(day, "%Y-%m-%d"),
                "semana_ano": datetime.strftime(day, "%W")
            }
        )

        day += timedelta(days=1)

    # Por fim, mostramos no console o resultado do sorteio
    sorted_list = sorted(list_sorteio_fds, key=lambda x: x["semana_ano"])
    
    df = pd.DataFrame(sorted_list)

    print("Fins de semana sorteados:")
    print(tabulate.tabulate(df, headers='keys', tablefmt='psql'))
    print("\nTotais:")
    # print(df["familia"].value_counts())
    df_summary = df.groupby(["familia"]).size().reset_index(name="qtd_fds")
    print(tabulate.tabulate(df_summary, headers='keys', tablefmt='psql'))

if __name__ == "__main__":
    main()