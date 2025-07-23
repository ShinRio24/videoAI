taget = 200

for a in range(200):

    for b in range(200):
        if (a)*(2**b)>200 and (a+1)*(2**b)-1<500:
            print(a,b, (a)*(2**b), (a+1)*(2**b)-1)

