import pandas as pd
import numpy as np
import math
from scipy.optimize import minimize
from pointGroup import PointGroup


class GirderGroup(object):
    """ Método construtor da classe """

    def __init__(self, pointGroup):
        self.pointGroup = pointGroup
        self.type = pointGroup.type
        self.centroids = None
        self.inOut = None

    """" Método para cálculo das coordenadas dos centroides dos berços """

    def computeCentroids(self):

        dataset = self.pointGroup.ptList
        pts_type = self.type

        # DataFrame que conterá os centroids ao final dessa função
        centroid_df = pd.DataFrame(columns=['Girder', 'x', 'y', 'z'])

        # variáveis auxiliares
        i = 0
        x_list = {'pts_name': [], 'pts_val': []}
        y_list = {'pts_name': [], 'pts_val': []}
        z_list = {'pts_name': [], 'pts_val': []}

        while (i < dataset.iloc[:, 0].size):

            current_girder = dataset.index[i][:7]
            point_name = dataset.index[i][8:]

            # insere nas listas temporarias as coordenadas do primeiro ponto do berço
            x_list, y_list, z_list = self.append_values('centroid', x_list, y_list, z_list, dataset,
                                                        current_girder, point_name, i, pts_type)

            # começando a iteração sobre os outros pontos do mesmo berço
            j = i+1
            while (current_girder == dataset.index[j][:7]):
                point_name = dataset.index[j][8:]

                # insere nas listas temporarias as coordenadas do primeiro ponto do berço
                x_list, y_list, z_list = self.append_values('centroid', x_list, y_list, z_list, dataset,
                                                            current_girder, point_name, j, pts_type)

                # tratamento de exceção de menos de 4 pontos medidos nesse berço ...
                # verifica se não é o último ponto
                if ((j+1) < dataset.iloc[:, 0].size):
                    # verifica se o próximo ponto já é de um berço novo E se o berço atual não é do tipo
                    # B05 ou B09 E, finalmente, se existem menos de 4 pontos na lista de coordenadas
                    if(dataset.index[j+1][:7] != current_girder and
                       current_girder[4:] != 'B05' and current_girder[4:] != 'B09' and
                       len(x_list['pts_name']) < 4):
                        print("exceção encontrada no berço "+current_girder +
                              ": menos de 4 pontos medidos p/ se calcular o X e Z do centroide.")

                        if (current_girder[4:] == 'B11'):
                            pts_list = ['C09', 'C10', 'C11', 'C12']
                        else:
                            pts_list = ['C01', 'C02', 'C03', 'C04']

                        for pt_name in pts_list:
                            if (not pt_name in x_list['pts_name']):
                                missing_pt = pt_name
                                break

                        # x_list = z_list = [C02, C03, C04]
                        if (missing_pt == 'C01' or missing_pt == 'C09'):
                            x_list['pts_val'] = [
                                np.mean([x_list['pts_val'][0], x_list['pts_val'][1]]), x_list['pts_val'][2]]
                            z_list['pts_val'] = [
                                np.mean([z_list['pts_val'][1], z_list['pts_val'][2]]), z_list['pts_val'][0]]
                        # x_list = z_list = [C01, C03, C04]
                        elif (missing_pt == 'C02' or missing_pt == 'C10'):
                            x_list['pts_val'] = [
                                np.mean([x_list['pts_val'][0], x_list['pts_val'][2]]), x_list['pts_val'][1]]
                            z_list['pts_val'] = [
                                np.mean([z_list['pts_val'][1], z_list['pts_val'][2]]), z_list['pts_val'][0]]
                        # x_list = z_list = [C01, C02, C04]
                        elif (missing_pt == 'C03' or missing_pt == 'C11'):
                            x_list['pts_val'] = [
                                np.mean([x_list['pts_val'][0], x_list['pts_val'][2]]), x_list['pts_val'][1]]
                            z_list['pts_val'] = [
                                np.mean([z_list['pts_val'][0], z_list['pts_val'][1]]), z_list['pts_val'][2]]
                        else:  # x_list = z_list = [C01, C02, C03]
                            x_list['pts_val'] = [
                                np.mean([x_list['pts_val'][1], x_list['pts_val'][2]]), x_list['pts_val'][0]]
                            z_list['pts_val'] = [
                                np.mean([z_list['pts_val'][0], z_list['pts_val'][1]]), z_list['pts_val'][2]]

                j += 1
                if (j >= dataset.iloc[:, 0].size):
                    break

            # cálculo dos centroids
            centr_data = pd.DataFrame(data=np.array([[current_girder, np.mean(x_list['pts_val']).round(4), np.mean(y_list['pts_val']).round(4), np.mean(z_list['pts_val']).round(4)]]),
                                      columns=['Girder', 'x', 'y', 'z'])
            centroid_df = centroid_df.append(centr_data, ignore_index=True)

            i = j
            x_list = {'pts_name': [], 'pts_val': []}
            y_list = {'pts_name': [], 'pts_val': []}
            z_list = {'pts_name': [], 'pts_val': []}

        # torna os itens da coluna 'girder' nos índices do dataframe,
        # necessário para usar as funções de cálculo aritimético entre dataframes
        centroid_df = centroid_df.set_index('Girder')

        # retorna o df com os termos no tipo numérico certo
        self.centroids = centroid_df.astype('float32')

    """ Método para cálculo das coordenadas de entrada e saída de cada berço """

    def computeInOut(self):

        dataset = self.pointGroup.ptList
        pts_type = self.type

        # DataFrame que conterá os centroids ao final dessa função
        inout_df = pd.DataFrame(
            columns=['Girder', 'x_in', 'y_in', 'z_in', 'x_out', 'y_out', 'z_out'])

        # variáveis auxiliares
        i = 0
        # modelo: [[x_in1, x_in2, ...], [x_out1, x_out2, ...]]
        x_list = [[], []]
        y_list = [[], []]
        z_list = [[], []]

        while (i < dataset.iloc[:, 0].size):

            current_girder = dataset.index[i][:7]
            point_name = dataset.index[i][8:]

            # insere nas listas temporarias as coordenadas do primeiro ponto do berço
            x_list, y_list, z_list = self.append_values('inOut', x_list, y_list, z_list, dataset,
                                                        current_girder, point_name, i, pts_type)
            # começando a iteração sobre os outros pontos do mesmo berço
            j = i+1
            while (current_girder == dataset.index[j][:7]):
                point_name = dataset.index[j][8:]

                # insere n
                x_list, y_list, z_list = self.append_values('inOut', x_list, y_list, z_list, dataset,
                                                            current_girder, point_name, j, pts_type)

                # tratamento de exceção de menos de 4 pontos medidos nesse berço
                if ((j+1) < dataset.iloc[:, 0].size):
                    total_points = len(x_list[0]) + len(x_list[1])
                    if(dataset.index[j+1][:7] != current_girder and
                       current_girder[4:] != 'B05' and current_girder[4:] != 'B09' and
                       total_points < 4):
                        x_list_in = x_list[0]
                        x_list_out = x_list[1]
                        # verifcação das características das listas de coordenadas em x e y
                        # para computar qual das quinas está faltando, considerando que apenas
                        # 1 ponto está faltando. Modelo que me baseei:
                        # --------------------------------------------------
                        #   [quinas existentes]  | x_list (apenas o sinal)
                        # --------------------------------------------------
                        #       [1,2,3]          |        [[-,+],[+]]
                        #       [1,2,4]          |        [[-,+],[-]]
                        #       [1,3,4]          |        [[-],[+,-]]
                        #       [2,3,4]          |        [[+],[+,-]]
                        # --------------------------------------------------
                        if (total_points == 3):
                            error_text = "exceção encontrada no berço "+current_girder + \
                                ": apenas 3 pontos medidos p/ se calcular a entrada/saída. "
                            if (len(x_list_in) == 1):
                                if (x_list_in[0] > 0):  # caso 4: faltando o C01 do berço
                                    error_text += "Ponto faltante: C01"
                                    # tratativa tipo 1: inserir na sublista 'in' de x_list, y_list e
                                    # z_list o ponto C0X_new = [C04(x), C02(y), C02(z)]
                                    C0X_new = [x_list[1][1],
                                               y_list[0][0], z_list[0][0]]
                                    inout_index = 0

                                else:  # caso 3: faltando o C02
                                    error_text += "Ponto faltante: C02"
                                    # tratativa tipo 2: inserir na sublista 'in' de x_list, y_list e
                                    # z_list o ponto C0X_new = [C03(x), C01(y), C01(z)]
                                    C0X_new = [x_list[1][0],
                                               y_list[0][0], z_list[0][0]]
                                    inout_index = 0

                            else:
                                if (x_list_out[0] > 0):  # caso 1: faltando o C04 do berço
                                    error_text += "Ponto faltante: C04"
                                    # tratativa tipo 3: inserir na sublista 'out' de x_list, y_list e
                                    # z_list o ponto C0X_new = [C01(x), C03(y), C03(z)]
                                    C0X_new = [x_list[0][0],
                                               y_list[0][0], z_list[0][0]]
                                    inout_index = 1

                                else:  # caso 2: faltando o C03
                                    error_text += "Ponto faltante: C03"
                                    # tratativa tipo 4: inserir na sublista 'out' de x_list, y_list e
                                    # z_list o ponto C0X_new = [C02(x), C04(y), C04(z)]
                                    C0X_new = [x_list[0][1],
                                               y_list[0][0], z_list[0][0]]
                                    inout_index = 1

                            x_list[inout_index].append(C0X_new[0])
                            y_list[inout_index].append(C0X_new[1])
                            z_list[inout_index].append(C0X_new[2])

                            print(error_text)

                        elif (len(x_list_in) == 2):
                            error_text = "exceção encontrada no berço "+current_girder + \
                                ": apenas 2 pontos medidos p/ se calcular a entrada/saída. "

                            """ tratativa para 2 pontos? """

                            print(error_text)

                j += 1
                if (j >= dataset.iloc[:, 0].size):
                    break

            x_list_in = x_list[0]
            y_list_in = y_list[0]
            z_list_in = z_list[0]
            x_list_out = x_list[1]
            y_list_out = y_list[1]
            z_list_out = z_list[1]

            # cálculo das coordenadas de entrada e saída
            inout_data = pd.DataFrame(data=np.array([[current_girder, np.mean(x_list_in).round(4), np.mean(y_list_in).round(4), np.mean(z_list_in).round(4),
                                                      np.mean(x_list_out).round(4), np.mean(y_list_out).round(4), np.mean(z_list_out).round(4)]]),
                                      columns=['Girder', 'x_in', 'y_in', 'z_in', 'x_out', 'y_out', 'z_out'])
            inout_df = inout_df.append(inout_data, ignore_index=True)

            i = j
            x_list = [[], []]
            y_list = [[], []]
            z_list = [[], []]

        # torna os itens da coluna 'girder' nos índices do dataframe,
        # necessário para usar as funções de cálculo aritimético entre dataframes
        inout_df = inout_df.set_index('Girder')

        # retorna o df com os termos no tipo numérico certo
        self.inOut = inout_df.astype('float32')

    """ Método auxiliar para checar o tipo do berço a partir de seu nome """
    @staticmethod
    def checkGirderType(girderName):
        if (girderName[4:] == 'B03' or girderName[4:] == 'B11'):
            girderType = 'B1'
        elif (girderName[4:] == 'B05' or girderName[4:] == 'B09'):
            girderType = 'B2'
        else:
            girderType = 'multi'
        return girderType

    """ Método auxiliar que faz as tratativas de seleção de pontos que irão compor os cálculos
    dos centroides e das coordenadas de entrada e saída """
    @staticmethod
    def append_values(calc_operation, x_list, y_list, z_list, dataset, current_girder, point_name, index, pts_type):

        # criação de listas de coordendas separadas(x, y e z) para cálculo do centróide segundo algumas exceções
        if (current_girder[4:] == 'B03' or current_girder[4:] == 'B11'):
            if (calc_operation == 'centroid'):
                if (len(point_name) == 3):
                    x_list['pts_name'].append(point_name)
                    z_list['pts_name'].append(point_name)
                    x_list['pts_val'].append(dataset.iloc[index, 0] * -1)
                    z_list['pts_val'].append(dataset.iloc[index, 2])
                elif (len(point_name) >= 6):
                    y_list['pts_name'].append(point_name)
                    y_list['pts_val'].append(dataset.iloc[index, 1])

            elif (calc_operation == 'inOut'):
                """ A DEFINIR """
                # temporario...
                if (point_name[-2:] == 'B1'):
                    x_list[0].append(dataset.iloc[index, 0] * -1)
                    y_list[0].append(dataset.iloc[index, 1])
                elif (point_name[-2:] == 'MR'):
                    x_list[1].append(dataset.iloc[index, 0] * -1)
                    y_list[1].append(dataset.iloc[index, 1])
                else:
                    z_list[0].append(dataset.iloc[index, 2])
                    z_list[1].append(dataset.iloc[index, 2])
            else:
                # caso do cálculo de todos os DoFs
                x_list['pts_name'].append(point_name)
                y_list['pts_name'].append(point_name)
                z_list['pts_name'].append(point_name)
                x_list['pts_val'].append(dataset.iloc[index, 0] * -1)
                y_list['pts_val'].append(dataset.iloc[index, 1])
                z_list['pts_val'].append(dataset.iloc[index, 2])

        elif (current_girder[4:] == 'B05' or current_girder[4:] == 'B09'):
            if (calc_operation == 'centroid'):
                if (pts_type == 'nominal'):
                    if (len(point_name) >= 6):
                        x_list['pts_name'].append(point_name)
                        y_list['pts_name'].append(point_name)
                        z_list['pts_name'].append(point_name)
                        x_list['pts_val'].append(dataset.iloc[index, 0] * -1)
                        y_list['pts_val'].append(dataset.iloc[index, 1])
                        z_list['pts_val'].append(dataset.iloc[index, 2])

                elif (pts_type == 'measured'):
                    if (len(point_name) >= 5):
                        x_list['pts_name'].append(point_name)
                        y_list['pts_name'].append(point_name)
                        x_list['pts_val'].append(dataset.iloc[index, 0] * -1)
                        y_list['pts_val'].append(dataset.iloc[index, 1])
                    elif (len(point_name) == 4):
                        z_list['pts_name'].append(point_name)
                        z_list['pts_val'].append(dataset.iloc[index, 2])

            elif (calc_operation == 'inOut'):
                if (point_name[-2:] == 'B2'):
                    x_list[0].append(dataset.iloc[index, 0] * -1)
                    y_list[0].append(dataset.iloc[index, 1])
                elif (point_name[-2:] == 'MR'):
                    x_list[1].append(dataset.iloc[index, 0] * -1)
                    y_list[1].append(dataset.iloc[index, 1])

                if (pts_type == 'measured'):
                    if (point_name[:2] == 'LV'):
                        z_list[0].append(dataset.iloc[index, 2])
                        z_list[1].append(dataset.iloc[index, 2])
                else:
                    z_list[0].append(dataset.iloc[index, 2])
                    z_list[1].append(dataset.iloc[index, 2])
            else:
                # caso do cálculo de todos os DoFs
                x_list['pts_name'].append(point_name)
                y_list['pts_name'].append(point_name)
                z_list['pts_name'].append(point_name)
                x_list['pts_val'].append(dataset.iloc[index, 0] * -1)
                y_list['pts_val'].append(dataset.iloc[index, 1])
                z_list['pts_val'].append(dataset.iloc[index, 2])

        else:
            if (calc_operation == 'centroid'):
                x_list['pts_name'].append(point_name)
                y_list['pts_name'].append(point_name)
                z_list['pts_name'].append(point_name)
                x_list['pts_val'].append(dataset.iloc[index, 0] * -1)
                y_list['pts_val'].append(dataset.iloc[index, 1])
                z_list['pts_val'].append(dataset.iloc[index, 2])
            elif (calc_operation == 'inOut'):
                if (point_name == "C01" or point_name == "C02"):
                    x_list[0].append(dataset.iloc[index, 0] * -1)
                    y_list[0].append(dataset.iloc[index, 1])
                    z_list[0].append(dataset.iloc[index, 2])
                else:
                    x_list[1].append(dataset.iloc[index, 0] * -1)
                    y_list[1].append(dataset.iloc[index, 1])
                    z_list[1].append(dataset.iloc[index, 2])
            else:
                # caso do cálculo de todos os DoFs
                x_list['pts_name'].append(point_name)
                y_list['pts_name'].append(point_name)
                z_list['pts_name'].append(point_name)
                x_list['pts_val'].append(dataset.iloc[index, 0] * -1)
                y_list['pts_val'].append(dataset.iloc[index, 1])
                z_list['pts_val'].append(dataset.iloc[index, 2])

        return x_list, y_list, z_list

    """ (Obsoleto) Método que calcula os desvios angulares de Roll, Pitch e Yaw de cada berço """
    @staticmethod
    def calculate_angles(girderGroup):

        ptList = girderGroup.pointGroup.ptList

        angles_df = pd.DataFrame(columns=['Girder', 'Roll', 'Pitch', 'Yaw'])

        i = 0
        pts_girder = []
        pts_name = []

        while (i < ptList.iloc[:, 0].size):

            current_girder = ptList.index[i][:7]
            point_name = ptList.index[i][8:]

            # adiciona na lista todos os pontos de um berço, exceto no caso de B03 e B11,
            # em que só será adicionado os pontos do multipolo
            if (current_girder[4:] == 'B03' or current_girder[4:] == 'B11'):
                if (point_name[-2:] != "B1" and point_name[-2:] != "MR"):
                    pts_girder.append(
                        [ptList.iloc[i, 0], ptList.iloc[i, 1], ptList.iloc[i, 2]])
                    pts_name.append(point_name)
            else:
                pts_girder.append(
                    [ptList.iloc[i, 0], ptList.iloc[i, 1], ptList.iloc[i, 2]])
                pts_name.append(point_name)

            # começando a iteração sobre os outros pontos do mesmo berço
            j = i+1
            while (current_girder == ptList.index[j][:7]):
                point_name = ptList.index[j][8:]

                # mesma regra se aplica
                if (current_girder[4:] == 'B03' or current_girder[4:] == 'B11'):
                    if (point_name[-2:] != "B1" and point_name[-2:] != "MR"):
                        pts_girder.append(
                            [ptList.iloc[j, 0], ptList.iloc[j, 1], ptList.iloc[j, 2]])
                        pts_name.append(point_name)
                else:
                    pts_girder.append(
                        [ptList.iloc[j, 0], ptList.iloc[j, 1], ptList.iloc[j, 2]])
                    pts_name.append(point_name)

                j += 1

                # se proximo ponto for o ultimo da lista,
                # sai do loop interno
                if (j >= ptList.iloc[:, 0].size):
                    break

            """ tratamento de exceção de menos de 4 pontos medidos nesse berço """
            # verifica se no caso do B1 e Multipolo há menos de 4 pontos
            if ((current_girder[4:] != 'B05' and current_girder[4:] != 'B09') and len(pts_girder) < 4):
                error_txt = "exceção encontrada no berço "+current_girder+": "
                if (len(pts_girder) == 3):
                    error_txt += "3 pontos medidos p/ se calcular os erros angulares."

                    if (current_girder[4:] != 'B11'):
                        pts = ['C01', 'C02', 'C03', 'C04']
                    else:
                        pts = ['C09', 'C10', 'C11', 'C12']

                    if(not pts[0] in pts_name):
                        # coordenadas do C01/C09 construido: [C04(x), C02(y), C02(z)]
                        # ** assume-se novamente que os pontos estão ordenados!
                        pt_C01_C09 = [pts_girder[2][0],
                                      pts_girder[0][1], pts_girder[0][2]]
                        pts_girder.append(pt_C01_C09)
                        pts_name.append(pts[0])
                    elif (not pts[1] in pts_name):
                        # coordenadas do C02 construido: [C03(x), C01(y), C01(z)]
                        pt_C02_C10 = [pts_girder[1][0],
                                      pts_girder[0][1], pts_girder[0][2]]
                        pts_girder.append(pt_C02_C10)
                        pts_name.append(pts[1])
                    elif (not pts[2] in pts_name):
                        # coordenadas do C03 construido: [C02(x), C04(y), C04(z)]
                        pt_C03_C11 = [pts_girder[1][0],
                                      pts_girder[2][1], pts_girder[2][2]]
                        pts_girder.append(pt_C03_C11)
                        pts_name.append(pts[2])
                    else:
                        # coordenadas do C04 construido: [C01(x), C03(y), C03(z)]
                        pt_C03_C12 = [pts_girder[0][0],
                                      pts_girder[2][1], pts_girder[2][2]]
                        pts_girder.append(pt_C03_C12)
                        pts_name.append(pts[3])

                elif (len(pts_girder) == 2):
                    error_txt += "2 pontos medidos p/ se calcular os erros angulares."
                    """ tratamento de exceção para apenas 2 pontos? """
                    pass

                print(error_txt)

            """ calculo dos angulos"""
            if (current_girder[4:] != 'B05' and current_girder[4:] != 'B09'):
                # operação necessária pois a lista pts_girder pode estar desordenada
                if (current_girder[4:] != 'B11'):
                    pts = ['C01', 'C02', 'C03', 'C04']
                else:
                    pts = ['C09', 'C10', 'C11', 'C12']

                index_C1 = pts_name.index(pts[0])
                index_C2 = pts_name.index(pts[1])
                index_C3 = pts_name.index(pts[2])
                index_C4 = pts_name.index(pts[3])

                # aqui C1 pode representar tanto C1 (caso dos multipolos) quanto C9 (caso dos B1)
                C1 = pts_girder[index_C1]
                C2 = pts_girder[index_C2]  # o mesmo se aplica para C2, C3 e C4
                C3 = pts_girder[index_C3]
                C4 = pts_girder[index_C4]

                roll_tan = (np.mean([C2[2], C3[2]]) - np.mean([C1[2], C4[2]])) / \
                    (np.mean([C1[0], C4[0]]) - np.mean([C2[0], C3[0]]))
                roll = math.atan(roll_tan) * 10**3  # em mrad

                pitch_tan = (np.mean([C3[2], C4[2]]) - np.mean([C1[2], C2[2]])) / \
                    (np.mean([C3[1], C4[1]]) - np.mean([C1[1], C2[1]]))
                pitch = math.atan(pitch_tan) * 10**3  # mrad

                yaw_tan = (np.mean([C3[0], C4[0]]) - np.mean([C1[0], C2[0]])) / \
                    (np.mean([C3[1], C4[1]]) - np.mean([C1[1], C2[1]]))
                yaw = math.atan(yaw_tan) * 10**3  # mrad

            else:  # caso dos B2

                # considera-se que os pontos estão ordenados
                error = False
                try:
                    B2, B2MR, LV01, LV02, LV03 = pts_girder
                except ValueError:
                    print("exceção encontrada no berço "+current_girder +
                          " to tipo B2: menos de 5 pontos no total.\n Calculo de angulos falhou para esse berço")
                    error = True

                if(error):
                    # valor para não compremeter o plot
                    roll = pitch = yaw = 0
                else:
                    roll_tan = (np.mean([LV01[2], LV03[2]]) - LV02[2]) / \
                        (LV02[0] - np.mean([LV01[0], LV03[0]]))
                    roll = math.atan(roll_tan) * 10**3  # mrad

                    pitch_tan = (LV03[2] - LV01[2]) / (LV03[1] - LV01[1])
                    pitch = math.atan(pitch_tan) * 10**3  # mrad

                    # transladando B2 para a origem do frame
                    B2_new = np.array([[B2[0]], [B2[1]], [B2[2]]])
                    B2_new = PointGroup.translate(
                        B2_new, -B2[0], -B2[1], -B2[2], 'direct')
                    B2_new = [B2_new[0, 0], B2_new[1, 0], B2_new[2, 0]]

                    # aplicando o mesmo shift em B2MR, e rotacionando em 20 mrad
                    B2MR_new = np.array([[B2MR[0]], [B2MR[1]], [B2MR[2]]])
                    B2MR_new = PointGroup.translate(
                        B2MR_new, -B2[0], -B2[1], -B2[2], 'direct')
                    B2MR_new = PointGroup.rotate(B2MR_new, 0, 0, 20, 'direct')
                    B2MR_new = [B2MR_new[0, 0], B2MR_new[1, 0], B2MR_new[2, 0]]

                    yaw_tan = (B2MR_new[0] - B2_new[0]) / \
                        (B2MR_new[1] - B2_new[1])
                    yaw = math.atan(yaw_tan) * 10**3  # mrad

            # salvando angulos em DataFrame
            angle_data = pd.DataFrame(data=np.array(
                [[current_girder, roll, pitch, yaw]]), columns=['Girder', 'Roll', 'Pitch', 'Yaw'])
            angles_df = angles_df.append(angle_data, ignore_index=True)

            i = j
            pts_girder = []
            pts_name = []

        # torna os itens da coluna 'girder' nos índices do dataframe,
        # necessário para usar as funções de cálculo aritimético entre dataframes
        angles_df = angles_df.set_index('Girder')

        # retorna o df com os termos no tipo numérico certo
        return angles_df.astype('float32')

    """ Método para cálculo entre os deltas entre as coordenadas de entrada de um berço
    e as coord. de saída de seu antecessor """
    @staticmethod
    def calc_delta_inout(inout_df):
        inout_delta = pd.DataFrame(
            columns=['Girder', 'delta_x', 'delta_y', 'delta_z'])

        for i in range(inout_df.iloc[:, 0].size):
            cur_girder = inout_df.index[i]
            if (cur_girder == 'S01-B01'):
                ref_girder = 'S20-B11'
            else:
                ref_girder = inout_df.index[i-1]

            data_arg = np.array([[cur_girder, inout_df.loc[cur_girder, 'x_in'] - inout_df.loc[ref_girder, 'x_out'],
                                  inout_df.loc[cur_girder, 'y_in'] -
                                  inout_df.loc[ref_girder, 'y_out'],
                                  inout_df.loc[cur_girder, 'z_in'] - inout_df.loc[ref_girder, 'z_out']]])

            data_df = pd.DataFrame(data=data_arg, columns=[
                'Girder', 'delta_x', 'delta_y', 'delta_z'])
            inout_delta = inout_delta.append(data_df, ignore_index=True)

        inout_delta = inout_delta.set_index('Girder')
        return inout_delta.astype('float32')

    """ Método para calcular a diferença entre 2 ptLists ponto a ponto """
    @staticmethod
    def evalDiff_pointToPoint(ptListRef, ptListMeas):
        diff = ptListMeas.sub(ptListRef)
        return diff

    """ Método para gerar uma estrutura com a relação de berços e pontos (nomes e coordenadas) contidos neles """
    @staticmethod
    def generateGirderDictionary(ptList):
        girderDict = {'girder': [], 'x_list': [], 'y_list': [], 'z_list': []}

        # variáveis auxiliares
        i = 0
        x_list = {'pts_name': [], 'pts_val': []}
        y_list = {'pts_name': [], 'pts_val': []}
        z_list = {'pts_name': [], 'pts_val': []}

        # passando pela lista de pontos e estruturando dicionario
        while (i < ptList.iloc[:, 0].size):

            current_girder = ptList.index[i][:7]
            point_name = ptList.index[i][8:]

            # insere nas listas temporarias as coordenadas do primeiro ponto do berço
            x_list, y_list, z_list = GirderGroup.append_values('all-dofs', x_list, y_list, z_list, ptList,
                                                               current_girder, point_name, i, 'nominal')

            # começando a iteração sobre os outros pontos do mesmo berço
            j = i+1
            while (current_girder == ptList.index[j][:7]):
                point_name = ptList.index[j][8:]

                # insere nas listas temporarias as coordenadas dos outros pontos do mesmo berço
                x_list, y_list, z_list = GirderGroup.append_values('all-dofs', x_list, y_list, z_list, ptList,
                                                                   current_girder, point_name, j, 'nominal')

                j += 1
                if (j >= ptList.iloc[:, 0].size):
                    break

            girderDict['girder'].append(current_girder)
            girderDict['x_list'].append(x_list)
            girderDict['y_list'].append(y_list)
            girderDict['z_list'].append(z_list)

            i = j
            x_list = {'pts_name': [], 'pts_val': []}
            y_list = {'pts_name': [], 'pts_val': []}
            z_list = {'pts_name': [], 'pts_val': []}

        return girderDict

    """ Método para avaliar os desvios entre dois grupos de pontos a partir do bestfit entre eles
        e segundo regras intrínsicas a cada tipo de berço """
    @staticmethod
    def evalDiff_bestFit(ptList_ref, ptList_meas):

        header = ['Girder', 'Tx', 'Ty', 'Tz', 'Rx', 'Ry', 'Rz']

        # DataFrame que conterá os centroids ao final dessa função
        deviation = pd.DataFrame(columns=header)

        # gerando estruturas com pontos mapeados por berço
        refPoints = GirderGroup.generateGirderDictionary(ptList_ref)
        measPoints = GirderGroup.generateGirderDictionary(ptList_meas)

        # iterando sobre pontos medidos e aplicando bestfit
        for currentGirder in measPoints['girder']:
            # extraindo índice do berço atual *
            # * se todos os berços estiverem presentes em ambos os arquivos de entrada, os índices devem coincidir
            girderMeasIndex = measPoints['girder'].index(currentGirder)
            girderRefIndex = refPoints['girder'].index(currentGirder)

            # inicializando arrays para conterem pontos
            #   full = todos os graus de liberdade serão considerados no bestfit
            #   partial = composição de graus de liberdade
            ptsMeas_full = []
            ptsRef_full = []
            ptsMeas_partial = [[], []]
            ptsRef_partial = [[], []]

            # identificando tipo do berço
            girderType = GirderGroup.checkGirderType(currentGirder)

            # rotina para extrair apenas pontos com nomes que estejam definidos tanto nas medições quanto nos nominais
            for pointName in measPoints['x_list'][girderMeasIndex]['pts_name']:
                # verifica se ponto está em ambas as listas de pontos do atual berço
                if pointName in refPoints['x_list'][girderRefIndex]['pts_name']:
                    # salva o indice referente ao nome do ponto
                    ptMeasIndex = measPoints['x_list'][girderMeasIndex]['pts_name'].index(
                        pointName)
                    ptRefIndex = refPoints['x_list'][girderRefIndex]['pts_name'].index(
                        pointName)

                    # extrai as coordenadas do referido ponto, tanto pro nominal quanto pro medido
                    ptMeas = [measPoints['x_list'][girderMeasIndex]['pts_val'][ptMeasIndex], measPoints['y_list']
                              [girderMeasIndex]['pts_val'][ptMeasIndex], measPoints['z_list'][girderMeasIndex]['pts_val'][ptMeasIndex]]

                    ptRef = [refPoints['x_list'][girderRefIndex]['pts_val'][ptRefIndex], refPoints['y_list']
                             [girderRefIndex]['pts_val'][ptRefIndex], refPoints['z_list'][girderRefIndex]['pts_val'][ptRefIndex]]

                    # diferenciando grupos de pontos para bestfits que exijam composição de graus de liberdade
                    if (girderType == 'multi'):
                        # adicionando pontos às suas respectivas listas
                        ptsMeas_full.append(ptMeas)
                        ptsRef_full.append(ptRef)

                    elif (girderType == 'B1'):
                        # diferenciando conjunto de pontos para comporem diferentes graus de liberdade
                        if(pointName[-2:] == 'B1' or pointName[-4:] == 'B1MR'):
                            # DoFs: [Ty]
                            ptsMeas_partial[0].append(ptMeas)
                            ptsRef_partial[0].append(ptRef)
                        else:
                            # DoFs: [Tx, Tz, Rx, Ry, Rz]
                            ptsMeas_partial[1].append(ptMeas)
                            ptsRef_partial[1].append(ptRef)

                    elif (girderType == 'B2'):
                        # diferenciando conjunto de pontos para comporem diferentes graus de liberdade
                        if (pointName[:2] == 'LV'):
                            # DoFs: [Tz, Rx, Ry]
                            ptsMeas_partial[0].append(ptMeas)
                            ptsRef_partial[0].append(ptRef)
                        else:
                            # DoFs: [Tx, Ty, Rz]
                            ptsMeas_partial[1].append(ptMeas)
                            ptsRef_partial[1].append(ptRef)

            # Parâmetros iniciais para o minimize
            (Tx, Ty, Tz, Rx, Ry, Rz) = (0, 0, 0, 0, 0, 0)

            if (girderType == 'multi'):
                # definindo os parâmetros para esse berço
                params = np.array([Tx, Ty, Tz, Rx, Ry, Rz])
                dofs = ['Tx', 'Ty', 'Tz', 'Rx', 'Ry', 'Rz']

                # aplicando a operação de minimização para achar os parâmetros de transformação
                transfMatrix = minimize(fun=GirderGroup.calculate_transformation, x0=params, args=(ptsMeas_full, ptsRef_full, dofs),
                                        method='SLSQP', options={'ftol': 1e-06, 'disp': False})['x']

            elif (girderType == 'B1'):
                # primeira operação -> doFs: [Ty]
                params = np.array([Ty])
                dofs = ['Ty']

                partial1 = minimize(fun=GirderGroup.calculate_transformation, x0=params, args=(ptsMeas_partial[0], ptsRef_partial[0], dofs),
                                    method='SLSQP', options={'ftol': 1e-06, 'disp': False})['x']

                # segunda operação -> doFs: [Tx, Tz, Rx, Ry, Rz]
                params = np.array([Tx, Tz, Rx, Ry, Rz])
                dofs = ['Tx', 'Tz', 'Rx', 'Ry', 'Rz']

                partial2 = minimize(fun=GirderGroup.calculate_transformation, x0=params, args=(ptsMeas_partial[1], ptsRef_partial[1], dofs),
                                    method='SLSQP', options={'ftol': 1e-06, 'disp': False})['x']

                # juntando resultados em unica array
                transfMatrix = np.array(
                    [partial2[0], partial1[0], partial2[1], partial2[2], partial2[3], partial2[4]])

            elif (girderType == 'B2'):
                # primeira operação -> doFs: [Tz, Rx, Ry]
                params = np.array([Tz, Rx, Ry])
                dofs = ['Tz', 'Rx', 'Ry']

                partial1 = minimize(fun=GirderGroup.calculate_transformation, x0=params, args=(ptsMeas_partial[0], ptsRef_partial[0], dofs),
                                    method='SLSQP', options={'ftol': 1e-06, 'disp': False})['x']

                # segunda operação -> doFs: [Tx, Ty, Rz]
                params = np.array([Tz, Rx, Ry])
                dofs = ['Tx', 'Ty', 'Rz']

                partial2 = minimize(fun=GirderGroup.calculate_transformation, x0=params, args=(ptsMeas_partial[1], ptsRef_partial[1], dofs),
                                    method='SLSQP', options={'ftol': 1e-06, 'disp': False})['x']

                # juntando resultados em unica array
                transfMatrix = np.array(
                    [partial2[0], partial2[1], partial1[0], partial1[1], partial1[2], partial2[2]])

            girderDeviation = pd.DataFrame(data=np.array([[currentGirder, transfMatrix[0].round(4), transfMatrix[1].round(
                4), transfMatrix[2].round(4), transfMatrix[3].round(4), transfMatrix[4].round(4), transfMatrix[5].round(4)]]), columns=header)
            deviation = deviation.append(girderDeviation, ignore_index=True)

        # torna os itens da coluna 'girder' nos índices do dataframe,
        # necessário para usar as funções de cálculo aritimético entre dataframes
        deviation = deviation.set_index('Girder')

        # retorna o df com os termos no tipo numérico certo
        return deviation.astype('float32')

    ''' Função que será utilizada como entrada para scipy.minimize(), com objetivo de
        calcular os parâmetros da transformação via quadrados mínimos entre dois conjuntos de pontos;
        - A função retorna uma np.array com o quadrado da distância euclidiana entre pontos equivalentes;
        - "params" são parâmetros da transformação que serão calculados no scipy.minimize();
        - "args" é uma tupla com 3 objetos: (np.array de pontos medidos, np.array de pontos de referência, string definindo o modo)
        - As np.array de pontos devem estar ordenadas da mesma maneira, e as colunas devem ser [x, y, z, Rx, Ry, Rz]
        - A transformação pode ser calculada em três diferentes modos:
            full:  transforma todos os graus de liberdade
            level: transforma apenas Ty, Rx e Rz
            plane: transforma apenas Tx, Tz e Ry '''
    @staticmethod
    def calculate_transformation(params, *args):

        x0 = args[0]
        x_ref = args[1]
        dofs = args[2].copy()
        dofs_backup = args[2]

        x0 = np.array(x0)
        x_ref = np.array(x_ref)

        (Tx, Ty, Tz, Rx, Ry, Rz) = (0, 0, 0, 0, 0, 0)
        # ** assume-se que os parametros estão ordenados
        for param in params:
            if 'Tx' in dofs:
                Tx = param
                dofs.pop(dofs.index('Tx'))
            elif 'Ty' in dofs:
                Ty = param
                dofs.pop(dofs.index('Ty'))
            elif 'Tz' in dofs:
                Tz = param
                dofs.pop(dofs.index('Tz'))
            elif 'Rx' in dofs:
                Rx = param
                dofs.pop(dofs.index('Rx'))
            elif 'Ry' in dofs:
                Ry = param
                dofs.pop(dofs.index('Ry'))
            elif 'Rz' in dofs:
                Rz = param
                dofs.pop(dofs.index('Rz'))

        # inicializando variável para cálculo do(s) valor a ser minimizado
        diff = []

        for i in range(np.shape(x0)[0]):

            rot_z = np.array([[np.cos(Rz*10**-3), -np.sin(Rz*10**-3), 0],
                              [np.sin(Rz*10**-3), np.cos(Rz*10**-3), 0], [0, 0, 1]])
            rot_y = np.array([[np.cos(Ry*10**-3), 0, np.sin(Ry*10**-3)],
                              [0, 1, 0], [-np.sin(Ry*10**-3), 0, np.cos(Ry*10**-3)]])
            rot_x = np.array([[1, 0, 0], [0, np.cos(
                Rx*10**-3), -np.sin(Rx*10**-3)], [0, np.sin(Rx*10**-3), np.cos(Rx*10**-3)]])
            ROT = rot_z @ rot_y @ rot_x
            xr = np.dot(ROT, x0[i])

            xt = xr + np.array([Tx, Ty, Tz])

            if 'Tx' in dofs_backup:
                diff.append(((x_ref[i, 0]-xt[0])**2).sum())
            if 'Ty' in dofs_backup:
                diff.append(((x_ref[i, 1]-xt[1])**2).sum())
            if 'Tz' in dofs_backup:
                diff.append(((x_ref[i, 2]-xt[2])**2).sum())

        return np.sqrt(np.sum(diff))