#!/bin/bash
python3 - "$@" <<'PYTHON_SCRIPT_UNNOBA'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Descarga PDFs INDIVIDUALES desde el Digesto de la UNNOBA.

No crea archivos ZIP. Requiere Python 3 y conexión con digesto.unnoba.edu.ar.
Predeterminado: versión CON FIRMAS.

Ejemplos (en macOS):
    python3 ~/Downloads/descargar_pdfs_unnoba.py
    python3 ~/Downloads/descargar_pdfs_unnoba.py --tipo normal
    python3 ~/Downloads/descargar_pdfs_unnoba.py --tipo ambos
"""
import argparse
import base64
import csv
import http.cookiejar
import json
import re
import time
import zlib
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, build_opener, HTTPCookieProcessor

# Lista completa de documentos incorporada: no necesitás descargar otro archivo.
_DOCUMENTOS = (
    'c-pm{Pp@sqaoxWPp+QE1Sk+zq&wvpKl8hJ##6VUiHaxf{pJ^J@d%~lbfrEUcj55nG{$e@%okQMp-`TZm?K;Z?4I~`yTl}g2tg7y=^$-8^7hiw)<`;kUi&}>K'
    ';+Mbp%XfeI@%s;#|Ne(}KYaN9$FINp_y6<$i{JeAcYpli_y6zzeqqJF)N%RQ%g3+(<-7m!>36^TyRZK1fB((je)aq9S4DJOe)Ow9fAi0mU%mhE@lP+`Uw-s2'
    'fBDOwfB35}zx?LAZ{Pj!mk+=C@%{S`|Mc>!ci;T@tCx>oe)Hk$AOH03{pElE=Z`OcdiSe8|I45M^ChUizJ>J9-(9})!`ZKV_op}C`A=KKe|;3}5AVMI`nwPB'
    '-(CLFKm6i%KYab;yYFAV_~zXge|-1#`w!oL`1arb_siv1e|Y!p_b;FR%ol(B`0`IL|N7yJzxnR{<zMn2|JN^HQT73#tO&}=Lis5q0?Iyol=TG4x4ag>t024z'
    'jn^XaT0XCm<uw%Gr3f#jO;sgLRrPskdVEcQmms`^Hohild`+L1q<LA)OBcXP7mb&Zc$v%V=U`9sYQTE06X7*kyc%h}Z~l7!bFk-m0rOD@!fViYk>+Fb=i|@8'
    'p63PZkJ=GloyLo_KQ@1V{5jb3>ld&;YD0K6+WJM>AG^Ol{v7OiUV!vhMEWaD`gfA_@4oa`OY^D#FGSxfPv2J(uj=#4>-z%mLiD}z^nD@mDn75YzHi9-h3I>w'
    '>H9`nzuLk2mDcwSnU9FRSDL<Wr1{tm=3`pl8=xly(f2~r_eRna=IaT`>-!GyLiD}x^nE9dukQ0o>w5$8Awl%L(Dc2L@*(r{A<64|V1E=u-wRLQllI5v?~jt!'
    '_YKgig6Mmp>H9{~tIgM|lGgXF0lW}>FEoAsDI^B3=JQJHdqdWHMBfWd-y3PYw}bUQt?wI9FBC-I3r*iQQoXSG^+HMOdjslUg6Mmp>3bv9zs#?HNm}0<GQJRf'
    'FEo8`r1513<14T4<NUEMK;K_}MB_!uAI;4lUxPi(t2ThwM0nBkeI@OWwfVf#`o0c;*FbpD^nE4i`#OAHX?<Tiz^fy?X!^dA^hE7Gue83e1>n^XUNn7QN%>GM'
    'KCiUCuM^;92rrtxuOvNDr_U>`@2dd3D#DAV?<*;Ptm5-Z>w81yV?lV)^u3YhqaDo0w7#zf@KS^qP2X3NUajWy%IkY%J_^E%r|(Jg(GKQgTHn|ByrWJ;-%pyp'
    'ucY&i>YjJJ278_tkPl5n-%p;tC*?!c&xdAS-!Fg{qVFe9-;>UV>hgJ|^}QkU5z+UPrtgh3AMId1ruDr6`SwKg{iNx8BjwxX=i4)_?+c*sC!+5sP2U%izAwJM'
    'pJ{!sKz(8&`hL>%y^`t^>enY`THhBye@#T+Pny0jB>h!<{Wa72z98#8qVFe7-xtz)Uk=v$w7yqly+`!@r0IJlt@nDc-lz4w0{Uwp`hL*#y^{2o`uc06^?gBj'
    'A^LvM^nD@mDhIsM`n~}5=z-|_LDTnzRF5uxJ$j_|y#o4cAo_mL^u3bwm-_l^r1gCP>V*T*tAnRkN%g|w*9%8luNGi`9Ee^WG`(6#`(yF<$C1~oKz(%}dUf#h'
    'DyhC&{QBxh>s58v`&V3uTpcvIs-)#!50?A1TrEKQI1sryXmYiX(#PVbk0UKt3s7F|h+OS7xmrl&)#8^|ds?mvu-tb<u6CMS71DAq{&L^ba#fM>g~-)TldDP^'
    'UwSaU(sEURbf_b8wbSIPkkTRX)1jW0s{*X|9Vth5S~*%s>%I8veNUI81(07Ik@uY@?}a44#Ft+^E$;<Lw>u*5J5AmTNq>p2zj|8UE08{RMBaCryjN2CsDAp`'
    ')AC+`@<d1UeW&SrA(bb@FHdy+59r*aKxMxp(!cX6)uhV4`j!1I{}CvGL#2jf1&vq4CLJoNf2h>*SphKg8j=+>URFRFdg2egmd^^1A`qh522HgoNrmV^5h$zL'
    'bO9=)Az4&oWl`6Vp67M>jz7Lenir5oH6)8_oyKdCc==gW>uFv<7S)jX*cy%3Ao23EsFt6PfNE<<7S)W#Ym#{Rs;%X-C?G3nNEX$2SrjQN5I-wuH9fw7Dq};k'
    's8(p>tC7Z+UuA6hEDESHHYAH`yex`TWfZ^4*wUvYg6MlBRcf?UNl5x$4)lHYltd@6KN^w`87m*UhD4Z;)88L$rPnWDd>N7t*`%#sLR!E4@ntj33&<Z0(f7vF'
    '_m#xU&mS$V?<bHC8KUovrtc>yADVtXWO;oL=r2R`z47#YA&oCze_3AN1N8|*^u6))y^(nN^$D}|d<61sL-f5>+I%GC+tbgtEwAqZy=sWQH=e#%()jZAs+IKk'
    '0`hG`^t~x<e3A0)>F3*~X<o?qLiD`}jTdQr&4clk*Y|*4t%$y_Jbh2ntJBx3HLdR_peHJ#?<-B;Pm-RPzMiOQeLn$xUlDy@Y5IPW^!@bpea-88p#D`6eP4O{'
    'o>c#ue*LSa_5B3&YDM&YrRn=g(yP<gt2M3f2QnWKeP3z%evszlIGB%VeGiy2)Qaf)O4IiwQwH@-8D4`u&kLweR7Brbn!fL(`b78Z6E&^x2Qt18eP3z%o@9!p'
    '<6wNH_5DEhM?~LOn!X>T{c#-Zk7<1mm=@K7==(y`_axII^-YUjgFU}~0r^lt^nIb}dy=V)`ld3k!Jg)YG>I&TzArR=PihjW2TdYNTHhm0NDHFx3r*jXnvm*2'
    '6Vj5__ehi5g6R7~)Ayt%w|dazwxsnv(gX|f!>u$wTqQNZ(t{>gC9Us~riX~>ZKavsDyiwA9yC47n%<U%+@IJ?Z~HN?URkEMw~(IZwSC9obr<Y;UVy&eOmAae'
    'O5>#@Uh4Bo>ic5Ieay}DHs(dr_qULq=Vk7F%)4OEk1wDey_w#IyjZ5Uw~!d)tGK+frni@m0(x~by^VQI8m~^`)qP$w%?qd(Zl<>}uR-HgNxZ7hYoymNAm83h'
    'Z)0Aawth|0`ZaxCJw3hv{k56i#=IJBd>Ltcna``Gc>(#*W_la*G8(T&;?;a!mY$D5KD3$M#=I(RJ}%OHTt2Uw=7s19MBlSaZ*L(ncpd18lIDf%kBGi!ncm()'
    'V(>cHAM^Si(O-zZSDwD_Bwh#lOVYf6^<EHt&oaHeg~Z_HulHHg+sj7*Jt2s`XPMsKLSpdp^+eY6_VQ7no+F69XPMsKLSpdp>p7Cv_sIPmLG-=Q^!+5w$9XUx'
    'dzu$e&k;o5vrKPqAu)LQ^_;Bf?Pbsc^+G}PJ<Ig=77}AV`t?Fd>wDz>y&(EtX!?GV^!@bpy`=R$@_tAVeJ?b9KS}y)`ua=K`X0GoD2Tonn!cYTJuwgTL|We?'
    '?-c~m_d?V6lT`nje*H_*`X0DXUKXJ5%cAM~Ny@j~`{Z}Qp64Y1uZi%Y>HA62tL}S+yI@cA8Ux@p5MDHWKS=s(44+q8-;W9K>Ig5Iz8|FZYfPV4Uf)-MS3`L5'
    '^gXHm<-YH@3-<i@S^zIYc+vFzAnDbyd|r8duK=%#@Z#xvQa<Fq=erB`{P;rVV?lV)^!*^s$8j(p)B1iO`b!aBG<`ov`fD8Mue81&2JjMu7fs&}Qa&`y=ats?'
    'BhI(WMD+cn>H9&-w}+c=mzmc09oQcyqVFe7-*?jf*!}%+ruBVC#uuXRCr#gX()j8J<14T40X;DheLs2no}?#+uP0_&-*+G%nuxxiG=1Mm`B3-sp_$kBKz(8&'
    '`hN2CJ*hr1{QAU9>-!GWCnlorCr#gXQhlQP^@*(M?FF>Ee*Kr<{M{#9s^egMU4FGiu>FX{>l)JYye{AQoY!Np=f_tA#ut(gO<F$GN$0h_`Qs~{4|QaJMDn3Y'
    '%ZEB?f9wbQV>%z|Kt42)d}z}0p-#$&x}OitbUp;UuPp<~hXySl>ZJX#`}^a_=R-h!Vj%g@;N?T4`b78Z6C<Aw0rjte<U@m(50UC$-LHR*bUxI8e0w1I(4gf*'
    'jg)UUKi?kdd<f{LPzI6@4O%|bNcm9n^P!Q>hZ>;o2a*rb^y)Pv1}|UV=k;ns)-NO<8nk?<k=Czvuzsb_I~t(B2BPl=P2V??{%XGd8fkssfO_FT^!=de`$no4'
    'Hosmt_^xZ0zXzn21CjoNCjA>JwQPQBIpjY8r2(_JBUwSGWd%l>#pciAQ(nyQs00#*jwB47mM}C@!qEJL;gn4?JSqWg+>u<O({c$TX=C%X@hJyq7$vY)b|lT{'
    'v^2v=Yo+;X<tcM#7$u;nJCcEPS_WbyMQy&KKIQuiua!VCsw2rs=OrhkVpQ{sQKu}SVU$4KxFdN>=jAP=x^eUC#;4q(;Rz0u7&?;DbXrPdq!NSqC5BT*(lAOO'
    'o9;-q(`ng`k+Ny?v+15b%`hN4>_|$}X(^47vP1K;!=66PFksc&+@jktuT~l_Zy~LE=B;{n!Jg*@Bqy6&bj*vEoERxNvEuVeo@VGMz<k`?k7Hh>4CEHl)4aCt'
    '_`F7%7c#y&!mHDG6%wz5@zvA3fV#`(ejM{^G+svHWj?Q#<^`m&oBMIh%V@kBiC6P^S(+E1zc%;dm{+Cosw7_3=T+0Z5Is>4UWLX>NxTm9L`m}k68O#iIOe4^'
    'UP9s}J}=Gk5}=~FxgW>8gvCo1hnFm$mt=V<us<52?^*80w~z?D)ZZVo?#Gvp0(#XDea~_~zJ<i#<?B^T>w5)ixrXR_qv?AcBwoYkmDcwP=zBx-z0vf&lJvd$'
    '`rgv|UV;755PfeneXpebQT_eV()wNj{bh*0H=4dzlKxU(e_2}JD^RL7MBf`t-|Hmtnm(_zzE>b0GDP1SP2VdiA5uRbvb4TeAm27b-y2QeD=FVrKi{^zzDMRG'
    'qVJ8T?@9Af4(4N8-viz4OGWg3rRjSi%}4R)V@>OOz&)W<MBi7Mz88|d7hm7kw7v(rwU>(M`%2UILR!DXU%zTv-wTirRYc!cn!XoOJ|uoVlyyJW4s^FK718%B'
    '_v2eg&-3cbujkaXz6acxN=5X2rRjSi>3i|@eNF3oz@4L1MBi7Mz86ycOZ@s*P3wEW9j#PE-&dNx7gD}0e!gAP`W|qvDizW9m8S27RL>E=o>R}gM)>vjKmO_c'
    'haWy$`H__jQTi+&<XcFLmH%KRlk`prWJU#1`Ya#hTSyFEerA;QLB4zxSosU0^jSX0w~!dT{FOiJgRFfb;|o#xEFa`sNCaN<V0>kje)oN&f9_)<N15ccHAvfj'
    '#Nx&Ajo!Yq-^b)W*z@xds8kdrGh+Eh-$G){N54{0@|h7(sVGQhRCt*YX?!ieQjztIzI+tOybF>Uv3#R%Au)LQnRnJV`m!hjnRh`lBbIOUEhNTz?`Pgw-{{N#'
    '2|y*RAej-%H~JP5V|@9Qu&i(N<)c7mRFKSw<r{qqiNVXyjIzGbmqCm0Lh_+P%ZDb3*F4~r&W8{m1x4~9rR75$ABF8ZE-y{zLx2xVQ6wKynqHlxd}#XlkmmCt'
    'Ku;)=4=FDnBI$|g>j_QgLx8VbQAFP>P2W$_{y6>pQPcV!@dZ#s-z!buPg4DB`t>hO>wCcWt0<!Hm8S0}DIc1CKBQ@VkN9*bqVJWa?*~cW4`1JFTHhnSIg03e'
    'rRn=Ys(%f?{-tSskND;&qVJWa?<c9AGyQswru9AI)1ipISDL;bBz-@8eXnVKkNAEGqVI*K?*~bL4PSprTHg;qe+i=Rg{JQZNq-Gre@R;3BR(*K=zF2*`$5Ww'
    'hMx~fTHhl+FoNiNq3QcU(qF^ZUy|1Mh>w*Z`d(=IevtOZ;qQ-<*7t}{hamc1X!^dB^jG)wm!$PQ(&t_feJ?b9-%0sn_wz?d>wBaRxgh#pX!^dB^jG)wm!$PQ'
    ';yWRTz89Ll?<76Z5A;M{-y`!8(f7jB_oVqa4(4N8-vhp1x&VEzi>B{8Nl&=GUw6TtA729Sng}nRz9*e`xV}tx!JZ#q2JjjPFPgsZBz^Dtn%o6@p4R|)b%Ym9'
    '-*-~J?fO{V1$&-X1$Z@t7fs)HlD>C+I_`o!&uam^4B^Go_oRBX>x+38>}g(rPlv9G@S^GaM#_g=pN_j=&+|g|$Aa*p>H9|7AKStHnAZ0VS??9$Mbr0<wBEOa'
    '^**id0kZ^Mg7Bj0`$o!#T(g9`U{CV`x_s+I^!=pidn1i6^T*dr>wCaAM<=51Cr#fslAdV3o|tKU5BPrRMD+cn>H9{~6V2BXlkaVC`FjOGiAeuRlm3lV8gm^t'
    '?t(o(^nlcIBGP}-q<<r&md#HsXIlCLmQ6Yl=|5@GzmZBk%`f%LwDbr1=j%kI|D;KOBT0YrrGM5^TI)i#&WrT7V_v2#i{x8K&-1G8)1tdzPxG1xFGYB<q<<w{'
    '-Kq0{S62F)B2q&TUM%T<4e5Dam+$zzBt0Ji>AzVdhrC!8$+wUg^KrPmvKGl3YJk^7cum^)nxyeHeO@!Yeks6fAiM@`{Zi8Ur9Q8b9$!FdY_mv?d3D<O64Lk*'
    'pI1+>U%-05StQ528g2brr1i^R@3R)k+dm5MGK81W#@8T?uY>j8(&G!rw>OLAm{+BZuR<DM#pjjR_sDvW==;Ib_oVfH9jy0ReQ!Y1J{^d@XIUiQLL$sZw`t#9'
    'u;<q=WPBm|e(?0YlGd+-@s-#2Ks~1;`o8n@eJ9Pw?(*s@%?p^19ntqJN8?*a3|{_x?0J0;<U<|N_noKjCrRJ?`A{F}@dfDnj_7-qH}Neb#`yB}eedc05zwn0'
    '(f2F^;#)|J{n6K}J+1ErS?>{j-)Z`u)HK=TV7<@kdjm}Tv?KbSWhHzIiNLG)`o7on_yY7-NAx|*FZdP`V|@AgtLODSGQJRf-+B6;G`{3ud}(@rMDzrr?^&k6'
    'w~!e7<AI)#bUp-(uZHM*mMQQpBt|~ukFS=l-vdpiwITYx(dzf4Ce!9NnZ675yuJtOs}0fjji>KP_0{RuS6jY*59E&x(f5s4zbDmm)XyJVUf(0*3(@zDr|(JU'
    'wQ?}N()u1SA=QTHdzvY*kxWRf`1xbn6xaaM9c_rdr<np9$#loWzdw;S1vW)^A^M(X3T!0PFw+BG>H9eg(G!Tir<np*QtR@%4)jF2eh-*VYeV!s%@o*3rqfpZ'
    '{4s3`T!B_<YKXq4nF3c*E44cPdQRFDxB{(4)ewD8GX<`sR-<+L`(xS^xcE<%e`<|Cj;7<a*}M(fY%HXQ%H{E)@<XhrVflS2eui~47k>(XHWdr0D@A$iO7Rfu'
    '`I!i0LWX3H#>*T@Cu!5qgwl4?2H0t;A(<o1ZrVt8nkIhb%kr5cveF}&qwz9FQYIt^D}77PM?k3>k~z}srYotbbe+CZP1{YIBD|2yk!Cl24T+Hn9q>xu`~sTd'
    't09>q&2GAqn&Q{#SE4QdvI98THY9U2-pdZs&HL$}Y+L^37m^7fnWOP;evwYL^&k^Ui&fKDtQsIzS*!guAc9ymb;YWsVOa=EM+}SRA8-wb0n0pCI-WL$EXbVP'
    'EY0ijoUBT-G%ut%S=>2!7wqX_hP+POjOb!slg4Y2crBk-x;lZpR@f}fV_vk0NqVhN+}8?s!Jg)YoDOZ4<}oi;4p~U2L&ZHEx(oI^FQ6K|S(?YZ8jTlemvpPq'
    'cfp?JrO4|JMR?JSP?Yq#LzmAhZG=*g+W?ydd_2BrDvWd+pt!dI?t(qf3&^=Q3;38<rST#OF*oPF3-&xOpk}yPz{k7_jn^dcnm(_R<^`N?Zx-+|FQxISBwp3$'
    'mCd;ea+`cJevf(4&WA|1$%`E5`*hBY+-53BK14HqFQnT{MSOjqHhwS2>&JrRLp0;}LVEpJ#NQv&#_ux21IXSFa9vaX+G%gogj8Xb=^Q}b#d;c6?=dU^V6m1i'
    'A@wYm-d$Mfl?!=STaZk<@G@;uCZxWyFX>Dhd6!m@OuNuBZPL56B7S9}q%&=#uSr2N$3n}rNqtR<`jv^2&K!|@s|Cp%3oUab-CHf<E7g+E9D&ovf@F?`mpPIy'
    '=eX}+?t(o(zJN@-Aem#KWsanGFh%@KyQDKm<aSO$GRH#897(rxiujp!$!Cs;o<K6k!pj^<dO{BLL_Tu__D4lBN9ARXr2SF+{ZZGcGswSv|Lw;Mna{`pE59N+'
    'r1Ek|(#kLX%C9qB!v~bBB1)fj*sY|FkGg#2sw2${8DEIf*G}VANW2clS3fl~fAjM3<GYV9KYWG`C?6^!Vrf3`N@_l&%P$|Mec%;oW~hjWrTM@sshOcJzkHbX'
    'fmh`5l_DaR<^!*!$5*<15u5gbSETv2A|jUN1Fxj!+q(RuGVKGeNHZ`+L@dn*UP;Zsbou4!v=6)@%{v4Uu{0leB{lER<tIsLA9zKYfe9jAX+H2uY6hmu7yW4;'
    'ctxHt2qIl+KJZF<!l2V%@6$f;iafy*M7q*^;Fa_QOQ*knrG4NPd2B04k(%ZMucXJeI(@yG_JLRA34<W|p5_Cuq$dnI{ZumT1FuN4OhNQL%?Dmd%`$Z!?2l=E'
    'k2D_=MBmeV;FZ*TNT;6<rG4NPdHgPjzNh)XE9vpO&I3J>*7u0Hjv)G;<^!)Ja~++2K9u%>*AdT0S%AK$*}z{TBH$YCbWFRz>*xS2K;6?!;I9!eXt`oy<+Z&6'
    'v;b|tc+#G9v)uKGsc8pz9SxubD0`X#{52xR*m8ya%Io?9&;oS*;>mha1>b#{T+{CFIt-u%sCt_D`!yoQ*m9HXwD-G?3D5#GJ<a<48WDq*E9ukD?>YuR3sCel'
    '<M(Ss3|el&nD%|wj_55w&(mz*uMrVwbzg6#)%-wKc|gt6Oy92&F~*j^%BQt_2h`~Vv^>r7T}juYwY%zc=CynUXaQP&^0YiDQ5<ffnD%?uApk8v%hT-MmDE*E'
    'hg*i2X)WIYEk6M*Pjhs?M#Pwju9i<5x@!j%#00cF&CmTB5rdYiAkud3+5s&;0WD8+bH7H!pyg`$w3)khK+8`+%hSBvuMsh5xmteawLDO<nShp`JS|VE*bKK~'
    'GxJ&=P^S~n@{_0KN$Rw_>NIWRt_@k`0WD8+alb}Hpw;|UKCR^&piT#%<!K)7*N7OjTy>hZaMuRttpR9xnuGf_A_gs2Z>0^~wE;DV0cd%efBQ8e1}(P+k+yHw'
    '24vL((DF3*_G?58T5eW7@>(8H5ChQigQw+53ZlCTB5mES4NwpR(DF3r_G?6pvE?d=v~jyOK+6w6%hP<@uMsh5xmrGL+pZ1B69=H>X|C<ph#0ioJTYzBt_@kY'
    '04-1RY`;dtpyjVyc`XlA0|%hx2T#kBs)5a|2Br<$)qr)Y16rQu*M5zNK+D{9D{a@V2B^~xXn9&koNGi3TCO_HcEnj4HaTubr-`>FGmUkcxHzr#mO3qt?;<@v'
    'u7LVO2eKZTtNk@1#<+6p4{1|-H6ZKhK-NR^w7*8gpyg&gX-j)GK*x7L$I~3zuMsh5xjO!oLHqtge>FgLbwJV6oZ6Mt(O%6}U1_6sH9*mKK+)5D+LhGOUd>hX'
    'X`6O6peEP>MNe~SzedEM<<<n#Che*St&5^B$FvHqwVsl?8mrsYxTIU_DbQL^HjDO%7R{kuNuBl7?W|YQ2JH&8=#|Z&J)}ib^rQ~G>UQWYX?u1B8bHft&mPjE'
    '=~PnxXLb8Om$W&%0`>^9nX`wqXgZbTj-akPLP=Y*E6|KxHf#2f7Ogr@>cy^ZFZPl)W>>)4MK+`HkQPmylAK-Cb#^IPoAK#idHcB%u{9qohn0xZSiJ`)=fc~3'
    'yzll9>G?GaQ4a+eS2P_@awyT_tA{i#z>rEdJNA$kO~;e`sMPhNDlM<$fl5RJbbRCKcv2<8?U`CyUdID9K?8KW@pL??Cg^%mm9+h{Aa{}s(D5`Mb|KwK68BD0'
    'N!zdsa$0SGj;DEL3+c34+|%lkw#pXd)W-lFPjku^(y5QQr#{8{({_!5+#oSP(bF8Wg>-{N+#4k2lwr2V4Nw)Emukq(XxvCv67H?8Vn*Nw<l6@1L^KC&A)Wk-'
    'd-7jS8EAXlfXv$f%};aE7Se4Tac|?4w2`(T_jwJ_{4^hJA>HQ{_dah)+h_}NcgX<FPjk^0(%mI-?=F?JiMAlOpDUpGY5vASy8SHf?dMYSnjgrJDxhL3PsI)r'
    'EjL5Tn)MF98Qf1bFzY?6ff?)0#Nc#-8;_0P9wI$U${$v*q%P~b9+FaHoy`u;pc;>3>LJpzH@qe?0lSatHmGU#&x_NJak<?X)85Yu==~;}^>c`-u~1bGs_LRj'
    'o^7m!Y=Q=$BBeiz)0BR>J?Ya9#%m!HumY$m3l(PqE`I{n>;wd4`{rF7qAIKj*f<lgxu{BZR3WGoK*hSb%jrVDmX9jC0|J&1vN;xqsDy=zbIIBDgGjp-FQB`w'
    'Y-Ys~DwbFA;`G*CZfo7NQSkzdGi38A4pB|ksN#qP*EJ*UQM`a2>arQhhNuQ>RCUg%>Mp909aTViv;b<IWg)vb<`2vDen|VrE}(O|6hN&Pnp&TnQ8isu=guwu'
    '@b261Uq1bjFaG%P<)2>u^}`o`^WFQ)zu}t!hs;etofeup<;>0H&&{kl_1m?)apLkwUH>}Ghih?qwXDZhEuRN^nv;c`q=%eX{vwOhU1~ixm-;-=)0}F|sl}XF'
    '%U9><hh9BS$y&p(@QtD!<<CD=&{+BN;5=FxW?ro?oj?1{Gv0V1MI(wOvpAhI)??$0&jUTpsl}Wm=ETYeIaf{B<5kno13j%q5s3xVV_27R7stA7Eni|~>oI^2'
    'nG~QN!}0=O92c_XnvkW9z!%`2D+Q>>6k0uoqoiEx+`I?)MO?(J6e!5hEWoc35iXdDE6_FlP)vZLr~)+^n(g;BA_gtDESh!wUJJPOp+HrJ<@tRLh%gP+MU~YH'
    'h*^jNRT-t7p>kF%*DB<k*Y_J~1)O#%P?b?yTEjW*ayv1<MtT;Nf05{or^>MkWjU%W&LyJtc!%h-I8P5Ki7ACumqjbOaLS=w97@^D&wniN#<}5`63e$?aUKe+'
    '$9Dps#d)@pP~!Vlvf@et%ZmCM&-0apGQCPd)`xl_)@usf?@-qA#Bp9*(-#NX1qyL{QlNrPD-3hYo|fzNl&=gUmMIF<6O>g?;5eo%*D&QZ($lCA$qCdGlvPjQ'
    '7#FSKOU`UP0Wlp=pq`+tdIHCDU=4q*%0E~I&X)zKC-B~@lDb`}d%&FC0uiS*0g4H%`yCvgwdLBZX}aT#06U-n=`pQ^ijW%4h`R-*JE#bd9}AEl(;BD<>A|?T'
    '334_+MhtBQ(4Z^{%CWOuuA6OMfg&pva>JMfinCG;|1NfV_93K@11;L@BQ@j^|AJ$7Pyq*8f(TI7pyHfoxqiQC`RTs|e`B<BTzVO_(hKMM)Z-)Y&*D5y$zn<~'
    'q{PxvoVUxXId_7x);g=Tm{NFwgJr9;IB%9$bM7Uaveemq7T^7YnV$-Jb(XN8N3)yjoO7A}crNo0>FJR*;*k|zHe;FUEY5Su_4r)!vp7#vDlw(-NM_KEWH=?4'
    '=G^ei8tJT7V@lzX49i4kae6qd=G<Ex=_479DV2~CtJ2BosIZ!I7cXm^vn)OY?FT#FPw6;o%i}a{T8}-OJ`eQtXo`<PdyhG>E+BB4=B&q_IiCl5dOXDkq1|Fm'
    'tR<Xdl(Qavay}3AB&XhE<+QC%a;ThyX71HFuNiuGl#`^by}IvQ|4K>$Qlvz<bA0Rjqiy{|q^HN!j7bSVN?2oRa>mqjNlA80#iTYvuZR@O(5rKfjQem&W$nDW'
    'uQgvuO@I`sa?m+yvp=fMhe%J4DS%W5NOjhj;*c6Xsh(Y@;uXCE>r|($Q=ApOyDNH6uTvV5YQQ?xXzP@6#*})bvL+>Mg^$$g*4EM^_34kZdRjJ4gNgRoVB&3<'
    'r?q)p-Q0{x<WQSSqvd*>^5&zP(&vGmopr^}iNCsc*>FL9bqj!0uDb^G{In~NS@GwQo}PBGkg6I?J5~#v#(ACA9$%-u4fE`9l6bqT5;0=!b;8-}MD`g;b{xg&'
    'a2Ww3R(q1hd5_i}-=n<^^Yl21x46<HMl5wH#u-QZTU@p&N%I>hy)tSMBhs?nIL(vVWAmi9VV)gF8jH$e5hGH8u5*0v`lIdL+b~bhwK$n8C1S*?%?T%yle*6+'
    'S(s}rbd0JRNp9Air^Y!eZ;xl?Z^Jyx$l`rXqjAK#?bJA)!p-*gwd_r&?wbg|%I#WWxy|Z2**PA<{n0}BA=1;^TaSiQS%H+i{D8H+b<XzI_lDDJn5UPeaLSdr'
    '0!FNtc#U&~ptap8SF#WBT3<1v5iw%PZO+B|*4I9xtlTyMmL&m}C06QYoYc+4U6!(CO5gJK6;+urDpoJf&T+i$kA}Aok)EA-@o8omK@xZQ0cqxOjxyWWEe5=X'
    'dAj~K;^Cw#9!{)RQrCb8^|#>-CrvNp@o;L<Lf&W#IcGTa{o#}?=e9axM$wdG*-Kx8d7e=n`;5}pcH-;dYQT)6-P_?@5P$6P_Ymo6Qt@+xqpbJmzt6gUX`BZK'
    ')?HG`+_%>PEaO04$I5@N0X@Hr*W#ke=5=woskHj#r^ibBOOz~{OL^mzo7!Hv=|0SpjLZN=C1OMxO4neXW_0<?KBMF~vZgU3jTn)R<BW6V*_!S%((E{jYbZ@3'
    'M#36LoimR5KBHtpXYu{GVk=<8^3*oY<v1I2mr>SE+pNWmqBWa!<HR_3Da_hFqip$G!z0U5qH)CXGPwrx{Jy5P%jlGm$?j`9n*gmD(IS;ljMKl?rbBCHcer@<'
    'E+b+zSUVhN^=|vCclx40?SSw;*y65oRu-!v&ov-|@OE;PyGT!?0<L<=iczsz(p>{0pjsZPY)iUcfnz$E04i3Iw{ni@s=BDMSHTNV50?R;8ms~)rygFWiz>ZV'
    '0jDg|0aUDuO_g)XQpH7;uF=KMex(7VSdYj#Iq-VSfgd70J*a>K1Tg>=>y{Iz>f7sZQDrYWRRd5}099q7;#@4O=Az0bGx7aPT|oir@&i_pj+4yDt~`GY^Q=7Y'
    'J!Yg4BUS;bbL4sN`;3(C24_92-{}nUWm*?$<JbpT->u)Jn@C%1N2Md0hJ#iI=48pXKMhCvJfX#mqG`x_Fx@yF98KCjqih{m<E5$xbzo&ZLA(a@{5aD6r7HXW'
    '&`NlhPFu7du^t~@gL$4&DZ7laFAuH6Yj*1qqt0T)S+mRjnw`B~U{zv9En-B<Ta1(8S(SZ8Ejy0lHM?2F$XMfubDmK4*X(9lMl)s<?Q692O-@n8%G_s^-q!#|'
    '(Y{7I-{f4xG<6td_caag5@>Y3skHM=<=iFE-Ma*uKHn^{&bARTVx6=Uj?OOoI@{9KOQg_Sfa(eDiW8^MTm3?B_LWbq04fDgvHCbw&a1lWmoKv`xWp@XtzUln'
    'l{53EvfP%9)63svZw0>#^CY7>V?|j@#E3NOuE9Lb=<=C;MkUKA&fZE77_lCVS59l*I?FDj?1OQWxC)>vV8nW7U>t8(lfKI+`^doJ2ji+UV#K<a!g(-mdk@C%'
    '!#q9L;_OXF#AvYQTI0;Mw$Er}=UTiTX|!guE`wi#A<VV?^(cE2++@UzBx1zM-Z<VgCS#vbGJC5Q>Z8q)^pFwDkhF3d%vRf#M_D`4+AJm%%rw?XW#xE1)MmSc'
    'vf8NDn2-j9NSR3GWFocJT|$~Aq%omjC1SN2sGO@_weD{EE4>bdYxQROdq{|NSbL3yunz4m)!DP!8lR0^J{}Mv3CGGg8mYTSBd<}O9z#7Q6zE1)BZkU(j8b<W'
    'qs(j{hT2<9s0D;bM@QFKo+s3Ih4pONF|=Yr!Cp35dl|>Tq1xIdl-<iLtQKwVSBHdH-dB~=#-rM9v1p{%p?IYp!8$Z(>kwz9w%wI_WY?j%-I<J_n#O9}Q90et'
    'YTI3hvVA*r#92qZ%(CGV8kIE5lw((@V=wD?jq)U+61RifI-MO8BIRX;(+#fdb%VQ$^6V^AUGcG_tuJ*R_B@~4k4Tg48q)K#?ed-dw&(Z3zTx$omyaLceZ2hD'
    '*Y|?I{KbF!@WZzsU%vV97F(RHsZ|79rC}o_ZCcgERukAR|KrD(_g}yJ{@o9sjXVTlK@b+&$Ri=t1B8W!u&mhCNI&(v9ES*p(t2LrLVA9gTb{GgeXt(F-+uS;'
    '-PeEl@bO(dlgo;o3@(3B5r)cQ$ni7SzT-30rxw7n;?B>PKOzV=VPWI+f8M_1W0NPb0e1~_)-ONZPxi6(?MEzZoErz*clNQ}2kT+mg*69o$hZ03#;{n++cl);'
    'VO_rC!zvkAOM%nADF`gugjCXApv8yv<b<pXn2>^C6Bf40@zvPA<6@I1u?cXaQ`U^JU4BHuCY*bn+jl%{ufc{>(~)dyad~yl3pYFDX0$T>EuiN!ck9lIW=^pl'
    '9&DFSOU!Hl%m$5_keG?fZ16PhCEcAdzzzWHEP$M2{Ovm~!2aZ*i%*K?Yyh)HW7bK`y34FR$!q}3D!{C=m<<xM;WMkuiCSt5umAuH3t*`nfTg+s%X5RS#t$c^'
    '0gIcl7PrcIJh6SpV`fh-ZW2$_zF8O7LuR$Jtcz~}J<m+MiFz07nY3zYC_UOLA*jZ>-F1!U`6e*x2#>o+&tRH0RJBd)%TM{BkEt|P1DI<(Ph+}#W*^gCq-QXV'
    '*mlo07y1B`vDzsNj`QAFPJVtD=_yQc>tWm63H1=uWzQk${lV$HG|brp?;?dn#4fWqA+IZDcKHp787CVbUNU|cX_{H@Ber`6EW}ye1g`NAjIoDn_uLcHu`R&l'
    'F)~ywEElZBaW7hq$zw(&wD>Yl>47Wn<p(U+Ipw&{?K(WZhMAsqEiP0Si`wqmWHl+~7=~%tZ{$3mrFF@VVp>rHUfQ$p$$6YQoz~#v`LPxI^AwBP6&q`8ar}8y'
    '_S+TPv$U!JhaaZM6%5w>fm=w=U%?RX@Z&z%x8#2O_ycxxMJCYBLV&YxW1Sh@LLy+B)jRt(=gbJjR%R^gRYwDk+D2m?=W>+&_8s@AZL}w`Rp1o78-T4F3tJ_f'
    'f>-|(yxSqR6St(a0!O?R0a#f8mD4w5`;H5+(g2zO6SpFlR#;s!ZXpqF(~3WF_j_feM&LpKA{SX`w~?<Q5k}xT09bfacmdZ97INKS(WdYsP2uHVH&`TqI)M(Q'
    'vek!TfUHCG$>~$Nea8nlp4xja-;Ub@Z0`kQY?Fs=kgyFG+Z?os3-o&t<i4ZO?mH@{>&x~XA0TV%xX7URmb};nU^@iZwjYs3VCPhrw(sl%ybm^*xNlGifNFCP'
    '4^go!#BU)HP>GMK3T><ju**sZ0J7XcZXq!ME*IdwK}ZH*i$~yEE#!Ck4GCW(jlbrOzt>owrx#!3SYyTX#$wSUUF2xqMUJ~zpQjgRxob>-9_wOh<K(#8cU*dt'
    'H}>M0I|e{+(8eBV<`#G6jzOarKjm9ng({-QDp1`5BG6Np9<4s5E$)`EdIjjQ1YYB`OxV8T(xVCF)>cff0Q6W_Ca(bz=(Xk2E4*E!$Mh7Sr?g$8lXi{n(o^2L'
    '2aG)d=m~AzBaJ=v$DZ(JZoF$WK<_o0-fN^?qq)0A<LSK?>%9i(y++e}jimRQtM}Szz4w+_iHQLkuhBGKD<opYB{rTRW-Hzu3|QZcwZ2^gB0NV}?(Sf;_08f_'
    'pH+eNjnyIK77&A8_2^aF`et!A^;Ln{T4|5|I33lu@3`~^Z|t?0UI*yWUi>Z6Gt<>vdYwlvu0&O!j#p`K|2Q2%w(q#~8gJ%~m>y6KVBNO31;m)S!=-0Ddce#D'
    'ssWYuhH{c-?(}DF<<SH7T%a0IX%8qTY0sVho?Ce9UR;T)KsBH$ZQUb1v|nx|s_Ih;8F+lUfXAncw$GBzEX;p=y82VZdRQ}=189ITcnvTXshPv_i1E%TEbjO='
    '2ha**@LFMzRI%6Z%_i@hq5}O1I?&Uhvvgf0J$tTxe}dl5-=rw<i?3+_Cu4CcoL67lciboS?U_}rjF8wE8WI~U6YyI=1Y*M@HU_PZUg9&H(N|2bvnnNpbcR!!'
    'ORulzt|pe&V`dXzHfhW{iCK4<%_o_~`gZgIFdMXWO-SpSxXhls0$aw6nRS3!r>$(0w6aZ?S$~pQoP`cRXAGLoD5Na3cv<LOtXXF9>#$Mc)<>7$u$UQ%nYqkL'
    'c}jD{UEM|jG)JLn4pLXQ;&yd=jWtKCl$e+R#8~H9*MJDbN^yzFdHpXdJelvy;`UIBRl&UmL}(AS)N2p5jw`r-c=zr1FWXmNK5_8LNldN+<SLDvkjRNku2RU&'
    'xFs3TX{)n3ZQTMQkehBxvQ-%5H1>JzO967MeLy*0uiJNAa>|*l;Yn5Bn(;>DXw7)90WoIl@W{=X*$-;WsR5iCjZ-CYsxGG|^{k9|Cl~;;L1Q*ZJHc>wf}qs_'
    'IxAyet3CkrF=*<8WNszHTymC}m2u6n4?t@Sn${rI9L1|S-o<)`Q|#5$H;1c;6U*T077&3`b=9n`1gH4*TCc#oqutvO((5%5ms8EmJB?LC0p?wy%{wKj26a_K'
    'IX~}Kjb*6-(@sd!?i$bYt#hj@O6B~dTV=+O00k-}1$vF=c}Qitkk0GRr7ea8q=rIk!rVAbn41f!oQ5=KsG8b#h8DG8W}Ts3<9WUX^E9so^OGlNGcMA%?EozV'
    'Hd(+b2UvB1%_o747}x-S4HmG$0XAG<&z+sk1&pu`03#ipO-|N4mp{V#lOt@#z#0Iou}0YBjIikfd#=hb<BlCoff1&x5yolPF}-dbcafgh8RO<*ZR^$<niB}i'
    'oPYzVx{&1jna_w9cN-J1CLryGgR{5~cX79IUWks^kkYmntC2AQ>&5EexKR$zjPfqh-1;=)i(R&L*bjk`)~CU_*EPIrU3Zb5C@847()~BT{oNn0KJ~?XOxv%v'
    'zs~AheT#^3g7cu>A7VW*{o?2LrY#;#+E^YJoYAE2Xwv88!HD~^m>K}gSiqD6OkH61B(Qja*9riuEMS}kUfl&=>vP9kqYl77R}ueQ*75T-q~{l}%XfVL+}-o%'
    'Ggg09<CjAPc*(&sIl2Wzc#EL!%b|UnqtK^d_BbsxjRm}sM%Xo;=LLLs(?Zh}s2<<jsx#goE9;!TbFOW5@7C5`q~}15x2-_F`uNSe_b>1N?d4}opZbKp#q`x5'
    'e*3%M|N8fT|LdRrwy-oQ$As;tCLnH{ZxCT;@%`;l*AAy`iIROzpZtPIt5fG3arK{0xb}lg5HbrjY0=2dNJ&ZaHJIo9d2H=E&gjf@YVjqtqLGi0l15YGTu^JW'
    '@A{<Aj3>a7XY^xEmmiSE6UU6l)~?^vYnY#N`tkdhkKcXs^3A99d()yX-@Lrl>G5b%JD~JwX}m<h^86i~0X3WpkN1(DW@RFASLX|>>5r(XtcK3lV4fdQvge6)'
    '7v^b7HO^x;e}qFyENg_yNnq+@{_-Zu^NdQE9ZL&F604GTjpcbprR_0l>2Xvn9!D3=B*SMkSfc3~3&A93Zyb%1A4eK@e!MJr74V&7^}M}>^!#{IulM79uy2U{'
    'R3~@?C>}*y#{>ir%a~6&gK7JY52zdga!d>_|5(gw>x3DyVzt7&g~VXhT~_<OFn0%2697<00Cn1I6VhxGA5ez@l?4D21Q5&5@fs2VP+2}8fdN%u1Q{~Lj5ft8'
    'X#`b&1li0iM+GnkHDtCKZMKz48cfw^)ibOr!m1&x8f{#WSk(ho4PTi6gI+TPkkJOyBn>9tpw|osWB?#UNg7Q_ayqbW-|+$AN>TxJWQdY9nvztKI#OR9S-}AT'
    'QhPgHiUBDN5J_sQFSYkinDzkyYfwct|4Q5Zm9z$_zXnxYUss?QS&<#T(sq2#TbJ!SJ|J9Q1OCCL$P`oB6cf@mFa9>K@D!7{Teq4ZQ;hWv=oS*eP~Pj;eIG0^'
    'f`DyakSQj#DJG<CUi@ud;3*~+kD$7l=Z!-^WBU<n1Q}@rnKOd!gN*@|c$=@=>y;1?>-owpBm$r^TtNFTSoQ%G0FWSnga)XP02LpQB=T0N@p4qRHsc{HR-f@('
    'NCZ~ZTvinp)dFb7S|$Lf&^9!ZW)x2|-Uk~2Dr*4ib!iA7Qsv_o((|W9YxwJRY3FC#<%0`gWe6*yv05Zn%V%XEE6;m<4P+8lgj=O?n<Q=rldwL^tyh2>vbwW+'
    'QQkr#aO>6QhOh3x?VGxFo{Ryp@;MQbR1jY(6wNGNQvp_ptYS5tyoE#<OjCVUfvo!5_uqcJpm>X_0rO6g97Y!lRU^&2=FdA_uxOaTyi-I~u`Zn6LSl?1f8Oa#'
    '%{xF~DU$E8E}h;&VzBZBmX2pPKj1x2-JX=k+&YUJ=Q`Z>9iLmzj4=ZQmLeivX(HZ80?T}Xr43)O1OS96ccm%!DWpj#J|M%>KxE59B)ak>I%&%r2U}jnr6y2m'
    '5kwORt*%Kb{EGOM7Fo|O;|53tL8OAvq=J#8g85QGa#8^qW5_Bcyj99btJJ|5d%nI9bGt+kbG!VAws?`a4VT+%uz79@a5ID(ubxFp35WXJEHgKOyQ^ga>;L6P'
    'w49KnAeyTnUW3iA|G?aw$lRQ~^`A61&7Yg|$+=m99=MmkG7xUGV?s_B-0F70y$?24tR0z<9RWnk4?Af>_JawT$`9KBST%$dEkA6eT)GXPRqBwZO@I}$DNfp^'
    '*hsl_n?5T%Rcy%0R1iS4Q;9}W4eelMDw)Al8^B5tR!S>kk&1t{`K(e06mbKC%a;XVMLVD{(&?%#pOvIeqT{T(Ah)c_psCS8%BqK(RhO|ccVq;Zg9A~ZgLVZ('
    'NH@~NpM&H1><|!G15u!Zc5pFB0&DmJYdn2$F#xeO5MerK!gP?t*6_vF=uh8v=m0lFqz;-$?VTj(yU#5pQVp4#h)5kYk!qy5X$NyNRk^9iURe=Vw4;qm+AHh9'
    'URhy5zmUO%2>L-2^oul@*1=#pam@$;gsAwzyJjRL1#tjK@zX<K=|=9fm(G(4q@{cKOZSO8?ZCsM(h*I-vS7G{#27)<2lTWi0NRg~j%b3;yVyX|Qs!%^-k#P{'
    '2scC@becZsByRnH+tVkB4Oqw;k}EdaX+<L~WX)g58va~BfrV`AP!e@nE{#^CQPMpTtzMVq0(U66d<7^UZ=EDUKt@}!lvF<U9-Q0<8v`mp`FLxT5Cfvg@j@ye'
    '7xe+ba(u414yqFvK}tKUxrX#Spv!mMM&=V9K@(`Tp&b}O%4*tn3yA>8YqfD7YzPSOnN_U|090AkVUp8qah+!GgAD;y;9-q!jS^x&tP))%J*=s{`hd_^+{J*~'
    'j#`m5sIt}|<J@-KzT*Re*C6CjLARFVAs||hP12!4aSs*lgN*>`ECSeZ6vU2$R8+c!^t`Xc<vYF|N9L5c_IS3*b`LLNCA52Z*N_;?kvrRDp;r!c07nC|bs=qs'
    'fZFyWmbVM%Xkh!!KA`(x;|&eCv?5&*K&*QPm2_#PdY4x2gAGSekF6I~HpjdW5X&;}7Si)0sC)K{_rb=1fNqh}8Um=X0CBoSZr||%H5^a@02u<vXn+a{Q1Jm7'
    'KE)6~6#-OfQ;Y<t9ssH^AfUmY7&3y4Hi9?}{<M1y{_cYXrkDbNkZqpTBJvgzV~VK{sNjI&tV1fYi&fe##<4%xzT*O_Cw4JFNmpcwRo)_PBtYf^dh*=kGJlbQ'
    'g{<9`wstFNVCliYs?Tx*`jLwXvSJBs&lA#~C;p0s9*1ZHIz@;eD;De7>@B3{0k!Fi0)bbo)`84zdmkGEnk+yZSIO-=KA;H$0<NKo3<MC%ptNzWp>E&t0l}5F'
    'wvZ8os3uyatu4|BS_dPjoNnx+Exv}cRu4&Ce!~LAxrDQQ#{u;kYdnw?pkn|XmUL=LqN6??I5}zY)sQuTu`_97hjTGx`;JFvo)|k4(-DA<(8dmFjaG5#;3_D-'
    'K)O0Gb~<m}A<+?+PRGYi+{AV@fKH>);k2;bzT?q>J)zX%)<p}bi7Z-4#5j$Mw(od!@QR4d8PidKj?(B%5}oPNflocGg=ziT`mWj`9b2rntG9p%befaY-^Ci!'
    'iO+=AmU%^VXo;7RPK3-m5xR>trV}^SSzFo_(qUy?#%ZaueaEFU&Y#|2zNay$4uI-3P)Y)&E~uUX6}Qk?(g0A6wi=OkGOvNoU96`-6<}d902C_`vqD;!ioY;f'
    '29(7as{s3((DpauWUQC(xS;U;Eq*++wz^PAho&4kPiMC8xO8ykSb^0@0Xj70NGjZ0^;aWYImVCJ=UO41%Wr6#8fol!PuTBb1;$Re?#v0$nKU|;wC;Fjp?9$Y'
    'V`s*644^~Xz6L2L^UNOZVg<%dcp^3jFm?uS>=e@2DIT4HkDb_Oc8&(np=rcI8au@uI|IIhX7OR+>~Y3=`3;K>>8Q}UOQ*vbYkh0a^VP?1-o1Z$|8Flpv-xxq'
    '|CY^HfB5b1e*f#=|NXCTe~xwxUpdA++jp*H+(^#|<{IDfoK4~Z)M%JUcRXuxH!k??rq=j)a2hbZSl;rtfCzNNrDOQ?k{;6;0G&aj(@Au?O9wuMuexG7fasxJ'
    '?Yss=prgyBWBAyKH?9)b$S%L3jh#svJMP9+`uPhAH9jbu1&}{1FTPtq3{K*5YWOIM=U4&eSfR}^A<Z#y=U9Q~SeYT60i<1nmUdkOdY;bZI}V+Jr(I=POs4{L'
    'Sf#>iKm<C=Tsm;6u*46d$B0XXgVg}+77&4s_Z<2zR)9{pDvuWH!olhZa|?(;$6J*L+!97h+_!g>xS(<Q4U3ME)*W-#ow9H`C8h(6okANs9QT{;J1!l3?8FaR'
    'Mi~GdR!&h!&smE1oaHXom`(*|RtM;?RC6I+P$<=(SsfocGp5r3I*m4VCTZ+Umrld!#CiwN%7dnr3+WwHDX!i*p_R*s=>Tewb}{N25QENe={)<`Nn!`#zV%VB'
    'htO(gwNbwX^gJ~2{Dbde4TqG(KCgYd;~UYT-SHKU%j@<Xk4{gNI3(Wkdj&>OrHvxemM_KSRMAlcnBKN6OD%_RN@HcIB*$CV@b)g!2+eGvkZzk)jL@*8;x(S9'
    '(Of>`p@D_sv=$tEZLPY>(ZN??_366C@;nx6yT@JyZqYU37Pz+cGttBGvfVW1fEk?rx5I0HdlzYh=Cjw{JL6@`*JXdaT>g}>QgzZB@1LJ|?*|!n=Z-J%ZhcEW'
    'ofzzmlp>cclC<Df&fVSmcy;$plySrI5sVPgFJ*WmM265B-49Ne^6@Z2?t%pRN&s(c8}bOb4O(A`N$M-%zp-t*JJ61*oAJ|8+aA^io3pVV)=tjL(dj)Ly^AzL'
    'Gc-)ZZF@%%?L(}06xVp3--pz^eMrzz(`tC5;FCF?xC`%Pm1h~_U4wa=%jGkVEAM@n5fqEF?91Bq<)@QJXE$1x|8SrfC&RY6w;kPu89}KFXq`2Vw`gU}pldMC'
    '?@4Ry?a>NPpBk5kW!f<m)?shuREFzgVfamyA(Hq($hJ)%OF7ms;k*T@k556~L>VH9FD8ivNLW|4NOzKUt|YyQGD7m%snediEywDX<#WX;J^g&xv>#+RLgLF='
    'Vh?ivGxjvSKRJ4T?v4<JCym7o(QIp|I}c^s+<wHGJDkeO_MLs@b|35;K)bf83fT2p7le?|2$7Z-@8JJFScFjAjL^28!yzG7&*5803_|7-+V45MPY7rdZ`+;X'
    'kPvT&;xvihzT*<w->CKpNi2MAYs?rDVl`&Gg+w4E!zHxem@zt`tf~c|g{<0@wrXqP(9+`5(iAO;d#7xVNfBB?+x=PF|MY1|juw!DT0zz-)(O-tBm%AF&%|<O'
    'tpaA>c3&wb)M;xKY4(Xf`}S`v?OV~W3J_`tp+*}+Bpc9GeL@W<G&?{DS(6HHP3ojIsr!U*RVf{qWdfKH8}E#!b7tA)JDx?QNp_EmTgul37@<~HSIbJewN%|('
    'OZUM7<7rfYP(=t;+L<3|O&ZlFR8Pz}0|*s_P@&B@Bh5JT2^E}BTL2+N2+`K0#;FBdzT*>0u1RrkmCLsUp+(!{2J4u8__UI`d&K))oq#3t<wrDHr2THV``v4>'
    '$oez^LJc8AQ<a^R$9a7r?t=vg0acVbIzVW!G8184Y!QFPjT4zkLkJ;bXwb$`BN1u`gwBj1V3rL;Ne-HlWF3}>Kg-4mC27D)JrE^1XiCyZE4BG6^*Es<;|njB'
    '?;%QZ(3E5)Ww*8agw7~QWDFrna`2QSX$-Z4F{CHPPy+}d>T%H2V{N1{)O<oGDkKVIv>n;)J8idDQbwzOM%z#9_6Dp&9og+WZMQelI%NJj)KBd87N1Pk?d&!r'
    'L_52^hQuHwE}`J;*3Hp?lkVD(oxkyReo}?R{0d3Sol=Sbv#%j4pwU!-kY=Cwv#*sLtpd<8WHmS1YF<dRicibVtmZ(C+mOt}XqkzTYTV}6xa~w{(ty?6kQryR'
    '8P`awdGl9uJE6NPLI}~_yqkcPM5rDRN>*?csCQRnO{zSFNve0NU+=DG>PdhGuZY5|ym}HzgEwD;*Aoh}B7~4tyV6$eN+MJb2%T89D>BOvRY|-1CZuN$QV(Vs'
    'Tu&;i13SMUgjfz3w~(H{(ti1lOGr)-0`75FL3V!Ho&UwT$Gv^WCsc4kz%9Uwu15$7ixB4);PxG#kl=(?Jch~wY5|4ihH(ptKxnyRsH}w(0`{`f06kP#9*(z='
    '2!#B-thA03YQPw34I$K6gc@lKHGd4Xc47>5fRG`Cj5dZkX$*Crkl}=4Td>RbF1vj{B-FPbu?TUD!M5-06S@!fRE~CmE&#29(4y`9oQ!t+j!z5U`6qB2xon1f'
    'At9C{-z}u)2~F=d@_n!|A>>}0Y<(>vLc(fnQAqdNihHl^KG=|uc8T{j(F!z1QC2I(Ye<B~DAL@<C|XYtDgdE^5Gpi6g+!?Mgy3~Z+XTjtAY+K;<Jd^O6WjF1'
    'kfioCZSgIeHDg$d*2un*8cH|sj?G=Hz+mbC9>6YrvL;*WBs|^6b7HP(kMRJ0>8!3hw}1$Ew7Yl|#}hBstFIVOXZ5mgq@}vKOZ984$mELs<Qp)08g2A+(mLI}'
    'b^0~dbIUZ)#%XPR|07hizW=0FPHNt>qq|s7qKZ}aT!8J`qM>ReyX)rK`YiZ*|8}t}Hhlzq*E-F2t&@D$y6d~v#|b>~=;?s97_IO2H6R8acl6*_{j{vud94DD'
    'VwL8Sut+Wm%XMB0PGP-usK$4XXDNWa7)v@<&duZPJFdN0>QdHLwv7Fv0N<8D^KEG)cZue@OALHXD)G7O7=Urhpc%JtPGz_6xOh&iNu$Sj1i-^`p}ht~z%#mw'
    'C-wSKrG^u&Z-%{*TLR6n_ZkqvEuos{me7)@;!9awEk>m*#~ad>EOoDB-Nkwe)vB?P%T|#LNfnmMgmPRaTpJg>8ad-+q}3JMOw`4)nOGc~iRIZ$)YP5-8QUwg'
    't<zS>iBt-h9D9Y?U8j-?myyN{g{1X(3>mA6bdBfvmfzE}DzTm#Lu1CR(fb5AO%^9kYxHR@r&NVx#1H&!^QDhk$g_Ou2j_MF@E-TyMS6-;U*VB|opG!E%Wp{b'
    'CW~_3fBB5V={3@GoaTr*b$}BoJ-Np7Jf}HaPCdg3I7=#9<?Ya)fK_%Qog?iWBfSmtWXH|e!Qr9;j?D^qy*4?|vb67-72x}SD}aSVi!2;S1-EN3&ySnpSUBJ>'
    '9%9eU?Jmt>BYM^~n#!@;tYz22VgLTjZ+`sv!^<}>pUs~Zw_Xn{9B7aBl+<6m?Y3Swlu3zqaVhh#9X-u0yDZX;J=tO6_+;NP`N#hcm&wL$'

)

AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
OPENER = build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))

class VisorLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag in ('iframe', 'frame', 'embed', 'object', 'source', 'a'):
            for k in ('src', 'data', 'href'):
                if d.get(k):
                    self.links.append((tag, d[k]))
        if tag == 'meta' and d.get('http-equiv', '').lower() == 'refresh':
            m = re.search(r'url\s*=\s*[\"\']?([^\"\';]+)', d.get('content', ''), re.I)
            if m: self.links.append(('meta', m.group(1)))

def es_sitio_unnoba(url):
    parsed = urlparse(url)
    return parsed.scheme in ('http', 'https') and (parsed.hostname == 'unnoba.edu.ar' or (parsed.hostname or '').endswith('.unnoba.edu.ar'))

def obtener(url):
    req = Request(url, headers={
        'User-Agent': AGENT,
        'Accept': 'application/pdf,text/html,application/xhtml+xml,*/*',
        'Referer': 'https://digesto.unnoba.edu.ar/',
    })
    with OPENER.open(req, timeout=25) as resp:
        return resp.read(), resp.geturl(), resp.headers.get('Content-Type', '')

def obtener_pdf(url, tipo, visitados=None, nivel=0):
    if visitados is None: visitados = set()
    if url in visitados or nivel >= 6: return None
    if not es_sitio_unnoba(url): return None
    visitados.add(url)
    contenido, final, content_type = obtener(url)
    if contenido.lstrip()[:5] == b'%PDF-':
        return contenido
    if 'html' not in content_type.lower() and b'<html' not in contenido[:400].lower() and b'<iframe' not in contenido[:400].lower():
        return None
    html = contenido.decode('utf-8', errors='replace')
    parser = VisorLinks()
    parser.feed(html)
    referencias = []
    for tag, href in parser.links:
        u = urljoin(final, href)
        if not es_sitio_unnoba(u): continue
        # No mezclar los PDF normales con las versiones con firmas.
        if tipo == 'normal' and 'documento.frameim.php' in u.lower(): continue
        if tag not in ('frame', 'iframe', 'embed', 'object', 'source', 'meta') and '.pdf' not in u.lower(): continue
        referencias.append((0 if '.pdf' in u.lower() else 1, u))
    # Algunos visores abren el PDF con JavaScript en lugar de un iframe.
    for match in re.findall(r"[\"\']([^\"\']+\.pdf(?:\?[^\"\']*)?)[\"\']", html, flags=re.I):
        u = urljoin(final, match)
        if es_sitio_unnoba(u): referencias.append((0,u))
    for _, candidate in sorted(referencias, key=lambda item: item[0]):
        try:
            pdf = obtener_pdf(candidate, tipo, visitados, nivel + 1)
            if pdf: return pdf
        except Exception:
            pass
    return None

def documento_valido(ruta):
    if not ruta.is_file(): return False
    try:
        with ruta.open('rb') as f:
            return f.read(5) == b'%PDF-'
    except OSError:
        return False

def main():
    parser = argparse.ArgumentParser(description='Descargar PDFs individuales del Digesto UNNOBA sin crear ZIP.')
    parser.add_argument('--tipo', choices=('firmas', 'normal', 'ambos'), default='firmas',
                        help='Qué PDF descargar (por defecto: firmas)')
    parser.add_argument('--destino', type=Path, default=Path.home() / 'Downloads' / 'PDF_UNNOBA',
                        help='Directorio de descarga (por defecto: ~/Downloads/PDF_UNNOBA)')
    parser.add_argument('--limite', type=int, help='Solo descargar los primeros N documentos, para probar')
    args = parser.parse_args()
    destino = args.destino.expanduser()
    destino.mkdir(parents=True, exist_ok=True)
    docs = json.loads(zlib.decompress(base64.b85decode(''.join(_DOCUMENTOS))).decode('utf-8'))
    if args.limite is not None:
        docs = docs[:max(0,args.limite)]
    print('Documentos únicos:',len(docs))
    print('Versión:',args.tipo,'| Destino:',destino)
    print('Cada PDF se guarda individualmente; no se crea ningún ZIP.\n', flush=True)
    pendientes=[]
    for doc in docs:
        for tipo in (('normal', 'firmas') if args.tipo=='ambos' else (args.tipo,)):
            filename = doc['archivo']
            if tipo=='normal': filename=filename[:-4]+'_normal.pdf'
            pendientes.append((doc,tipo,filename))
    errores=[]
    exitos=0
    anteriores=0
    for i,(doc,tipo,filename) in enumerate(pendientes,1):
        ruta=destino / filename
        if documento_valido(ruta):
            anteriores += 1
            print(f'[{i}/{len(pendientes)}] Ya existe: {filename}',flush=True)
            continue
        print(f'[{i}/{len(pendientes)}] Descargando: {filename}',flush=True)
        fallo='No se encontró un PDF válido en el visor'
        for intento in range(1,4):
            try:
                data=obtener_pdf(doc[tipo], tipo)
                if data is None: raise ValueError('El enlace no devolvió un PDF reconocible')
                tmp=ruta.with_suffix('.pdf.part')
                tmp.write_bytes(data)
                tmp.replace(ruta)
                exitos+=1
                fallo=None
                break
            except Exception as exc:
                fallo=f'{type(exc).__name__}: {exc}'
                if intento < 3: time.sleep(1.5 * intento)
        if fallo:
            errores.append((doc['cod'],doc['titulo'],tipo,doc[tipo],filename,fallo))
            print('  ERROR:',fallo[:180],flush=True)
        time.sleep(0.2)
    if errores:
        with (destino/'errores_descarga.csv').open('w',encoding='utf-8-sig',newline='') as f:
            wr=csv.writer(f)
            wr.writerow(['codigo','titulo','tipo','url','archivo','error'])
            wr.writerows(errores)
    print(f'\nCompletado. Descargados: {exitos}; ya existían: {anteriores}; errores: {len(errores)}')
    print('Carpeta:', destino)
    if errores: print('Revisá errores_descarga.csv para detectar los que faltan. Podés volver a ejecutar el programa: no repite los PDF válidos.')

if __name__ == '__main__':
    main()

PYTHON_SCRIPT_UNNOBA
estado=$?
if [ -t 0 ]; then
    read -r -p "Presioná Enter para cerrar..." _
fi
exit "$estado"
