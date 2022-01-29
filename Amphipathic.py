from numpy import convolve, fft, mean, matrix, square
from matplotlib import pyplot, transforms


def read_table(table_name):
    table = {}
    fd = open("/.../tables/{table_name}", 'r')
    for line in fd:
        line = line.strip()
        (key, val) = line.split(" ")
        table[key] = val
    return table

def fourier(sequence, table, id_user, id_output):
    hydro = [table[aa] for aa in list(sequence)]
    window = 25
    km = [1/25] * 25
    Mean = convolve(hydro, km, 'same')
    y = 12
    b = -12
    S = []
    D = []
    ZERO = [0] * 25
    D = [ZERO] * 13
    while y <= (len(hydro)-(12)-1):
        while b <= 12:
            S.append((hydro[y+b]-Mean[y]))
            b += 1
        T = fft.fft(S)
        D.append(T)
        S = []
        b = -12
        y += 1
    Dn = D/mean(D)
    I = matrix(abs(Dn))
    I = square(I)
    pyplot.figure(figsize=(3, 7))
    pyplot.contourf(I[0:len(hydro)+12, 0:12])
    pyplot.xticks([25/3.6, 11], ["1/3.6", "1/2"])
    pyplot.grid(color='w', linestyle='-', linewidth=0.75)
    pyplot.savefig("Algo/{id_user}/{id_output}_Fourier.png")
    pyplot.figure(figsize=(3, 7))
    km = [1/15] * 15
    base = pyplot.gca().transData
    rot = transforms.Affine2D().rotate_deg(90)
    pyplot.plot(convolve(hydro, km, 'same'), 'r', transform=rot + base)
    pyplot.grid(color='b', linestyle='-', linewidth=0.75)
    pyplot.ylim([1, len(I)])
    pyplot.savefig("Algo/{id_user}/{id_output}_hydroplot.png")
