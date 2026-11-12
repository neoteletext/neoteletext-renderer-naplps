from _support import *
META=dict(number=32,title='Form in motion',purpose='Museum exhibition announcement',style='Asymmetric Bauhaus poster: primary circle, square and triangle',techniques=['native arcs','polygons','display type'],animated=False)
def build():
    p=Page('032-form-in-motion',['f2eddf','191c22','d33e31','254a9e','efc936'])
    p.rect(0,0,191,169,2)
    p.t(95,0,'M',137,164,c=1,align='center')
    p.t(220,15,'KERN MUSEUM',27,38)
    p.t(222,61,'14 NOV - 28 FEB',20,28)
    p.circle(467,206,118,3)
    p.rect(299,111,36,36,1)
    p.t(18,190,'FORM',65,86)
    p.t(19,279,'IN MOTION',42,58)
    p.t(22,355,'DESIGN 1919-1933',22,31)
    p.poly([(395,480),(640,480),(640,327)],4)
    p.t(22,407,'Objects. Colour. Space.',20,28)
    p.t(22,444,'TUE-SUN 10-6',20,28)
    return p
if __name__=='__main__':run(build)
