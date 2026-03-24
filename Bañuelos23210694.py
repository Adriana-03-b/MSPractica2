# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 16:08:22 2026

@author: adrib
"""

"""
Práctica 1: Diseño de controladores

Departamento de Ingeniería Eléctrica y Electrónica, Ingeniería Biomédica
Tecnológico Nacional de México [TecNM - Tijuana]
Blvd. Alberto Limón Padilla s/n, C.P. 22454, Tijuana, B.C., México

Nombre del alumno: Adriana Estefania Bañuelos Ocampo
Número de control: 23210694
Correo institucional: L23210694@tectijuana.edu.mx

Asignatura: Modelado de Sistemas Fisiológicos
Docente: Dr. Paul Antonio Valle Trujillo; paul.valle@tectijuana.edu.mx
"""
# Librerías para cálculo numérico y generación de gráficas
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import control as ctrl
import pandas as pd

u = np.array(pd.read_excel('signal.xlsx',header=None))

x0,t0,tend,dt,w,h = 0,0,15,1e-3,10,5
N = round ((tend-t0)/dt) + 1
t = np.linspace(t0,tend, N)
u = np.reshape(signal.resample(u,len(t)), -1)

def cardio(Z,C,R,L):
    num = [L*R,R*Z]
    den = [C*L*R*Z,L*R+L*Z,R*Z]
    sys = ctrl.tf(num,den)
    return sys

#Función de tranferencia: Normotenso
Z,C,R,L = 0.033,1.5,0.95,0.01
sysnormo = cardio(Z,C,R,L)
print (f'Función de transferencia del normotenso (control): {sysnormo}')

#Función de tranferencia: Hipotenso
Z,C,R,L = 0.02,0.25,0.6,0.005
syshipo = cardio(Z,C,R,L)
print (f'Función de transferencia del hipotenso(caso1): {syshipo}')

#Función de tranferencia: Hipertenso
Z,C,R,L = 0.05,2.5,1.4,0.02
syshiper = cardio(Z,C,R,L)
print (f'Función de transferencia del hipertenso (caso2): {syshiper}')

#Respuestas en lazo abierto
_,Pp0 = ctrl.forced_response(sysnormo,t,u,x0)
_,Pp1 = ctrl.forced_response(syshipo,t,u,x0)
_,Pp2 = ctrl.forced_response(syshiper,t,u,x0)

fg1 = plt.figure()
plt.plot(t,Pp0,'-',linewidth=1,color= [0.54,0.52,0.20],label= 'Pp(t):Normotenso')
plt.plot(t,Pp1,'-',linewidth=1,color= [0.66,0.16,0.11],label= 'Pp(t):Hipertenso')
plt.plot(t,Pp2,'-',linewidth=1,color= [0.46,0.10,0.10],label= 'Pp(t):Hipotenso')
plt.grid(False)
plt.xlim(0,15); plt.xticks(np.arange(0,16,1))
plt.ylim(-0.6,1.4); plt.yticks(np.arange(-0.6-1.6,0.2))
plt.xlabel('t(s)')
plt.ylabel('Pp(t) [V]')
plt.legend(bbox_to_anchor=(0.5,-0.2),loc='center',ncol=3)
plt.show()
fg1.set_size_inches(w,h)
fg1.tight_layout()
fg1.savefig('Cardiovascular lazo abierto python.pdf')

#Controlador PID 
def controlador (kP,kI,kD,sys):
    Cr = 1e-6
    Re = 1/(kI*Cr)
    Rr = kP*Re
    Ce = kD/Rr
    numPID = [Re*Rr*Ce*Cr,(Re*Ce+Rr*Cr),1]
    denPID = [Re*Cr,0]
    PID = ctrl.tf(numPID,denPID)
    X = ctrl.series (PID,sys)
    sysPID = ctrl.feedback (X,1,sign=-1)
    return sysPID

hipoPID = controlador (1.494,352.001,0.000491,syshipo)
print (f'Función de transferencia del hipotenso en lazo cerrado: {hipoPID}')

hiperPID = controlador (161.301,38537.635,0.022,syshiper)
print (f'Función de transferencia del hipertenso en lazo cerrado: {hiperPID}')

#Respuestas del sistema de control en lazo cerrado
_,PID1 = ctrl.forced_response (hipoPID,t,Pp0,x0)
_,PID2 = ctrl.forced_response (hipoPID,t,Pp0,x0)



colors = np.array([
    [138, 134, 53],   
    [170, 43, 29],   
    [204, 86, 30]     
]) / 255.0

plt.figure(figsize=(10,6), facecolor='w')
plt.rcParams.update({'font.family':'Times New Roman'})

# Subplot 1: Normotenso vs Hipotenso
plt.subplot(2,1,1)
plt.plot(t, Pp0, '-', color=colors[0], linewidth=1, label=r'$P_p(t):Normotenso$')
plt.plot(t, Pp1, '-', color=colors[1], linewidth=1, label=r'$P_p(t):Hipotenso$')
plt.plot(t, PID1, ':', color=colors[2], linewidth=2, label=r'$PID(t):Hipotenso$')
plt.legend(fontsize=10, loc='upper center', ncol=3, frameon=False,
           bbox_to_anchor=(0.5, 1.25))  
plt.xlabel(r'$t$ [s]', fontsize=11)
plt.ylabel(r'$V_i(t)$ [V]', fontsize=11)
plt.xlim([0,15]); plt.xticks(np.arange(0,16,1))
plt.ylim([-0.5,1.3]); plt.yticks(np.arange(-0.5,1.21,0.2))
plt.title('Normotenso vs Hipotenso', fontsize=10)

# Subplot 2: Normotenso vs Hipertenso
plt.subplot(2,1,2)
plt.plot(t, Pp0, '-', color=colors[0], linewidth=1, label=r'$P_p(t):Normotenso$')
plt.plot(t, Pp2, '-', color=colors[1], linewidth=1, label=r'$P_p(t):Hipertenso$')
plt.plot(t, PID2, ':', color=colors[2], linewidth=2, label=r'$PID(t):Hipertenso$')
plt.legend(fontsize=10, loc='upper center', ncol=3, frameon=False,
           bbox_to_anchor=(0.5, 1.25))   
plt.xlabel(r'$t$ [s]', fontsize=11)
plt.ylabel(r'$V_i(t)$ [V]', fontsize=11)
plt.xlim([0,15]); plt.xticks(np.arange(0,16,1))
plt.ylim([-0.5,1.3]); plt.yticks(np.arange(-0.5,1.21,0.2))
plt.title('Normotenso vs Hipertenso', fontsize=10)

plt.tight_layout()
plt.savefig('Cardiovascular_PID.pdf', format='pdf')
plt.show()

