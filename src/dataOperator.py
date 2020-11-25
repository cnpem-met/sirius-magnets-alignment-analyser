import pandas as pd
import numpy as np


class DataOperator(object):
    """ Método que carrega dados em um dataframe a partir de planilhas excel,
        além de ordenar os dados e criar a coluna de índices com os nomes dos berços """
    @staticmethod
    def loadFromExcel(excel_file_dir, excel_sheet, has_header):
        key_column = 'Girder'
        if (has_header):
            header_val = 0
            names_val = None
        else:
            header_val = None
            names_val = ['Girder', 'x', 'y', 'z']

        # extraindo os dados das planilhas e alocando em Dataframes
        df = pd.read_excel(excel_file_dir, sheet_name=excel_sheet,
                           header=header_val, names=names_val)
        df_sorted = df.sort_values(by=key_column)
        df_sorted.reset_index(drop=True, inplace=True)
        df_sorted = df_sorted.set_index(key_column)

        # reordenando dataframe conforme ordem dos imãs *
        # *especialmente para o cálculo das distâncias entre os imãs
        # ** tratamento necessário apenas para o caso do berço 3
        newIndexList = []
        i = 0
        while i < len(df_sorted.index):
            index = df_sorted.index[i]
            if (index[4:7] == 'B03'):
                dipole = []
                isGirderB03 = True
                j = i
                while isGirderB03:
                    currentIndex = df_sorted.index[j]
                    nextIndex = df_sorted.index[j+1]
                    if (currentIndex[8:12] != 'QUAD' and currentIndex[8:12] != 'SEXT'):
                        dipole.append(currentIndex)
                    else:
                        newIndexList.append(currentIndex)

                    if (nextIndex[4:7] != 'B03'):
                        isGirderB03 = False
                        [newIndexList.append(dipolePoint)
                         for dipolePoint in dipole]
                    else:
                        j += 1
                i = j
            else:
                newIndexList.append(index)
            i += 1

        df_sorted = df_sorted.reindex(newIndexList)

        return df_sorted

    """ Método para salvar um dataset em uma planilha """
    @staticmethod
    def saveToExcel(excel_file_dir, data):
        data.to_excel(excel_file_dir)

    """ Método para atualizar um dataframe que tenha dados obsoletos; a função funciona substituindo as
        linhas do df do 2o argumento (updated_parcial...) nas linhas correspondentes no df do 1o argumento """
    @staticmethod
    def update_dataframe(old_fully_df, updated_parcial_df):

        new_fully_df = old_fully_df.copy()

        new_fully_df.loc[updated_parcial_df.index] = np.nan
        new_fully_df = new_fully_df.combine_first(updated_parcial_df)

        return new_fully_df
