import os
import subprocess

illinois = '/Users/cinjonresnick/Desktop/org/code/smacs/illinois'

def decrypt_pdf(from_dir, to_dir, name):
    #name should be in dir/src
    command = 'qpdf --decrypt %s %s' % (from_dir + name,
                                        to_dir + name)
    subprocess.call(command, shell=True)

def ghostscript_pdf_to_png(from_dir, to_dir, name):
    png_parts = name.split('.')
    png_parts[-1] = 'png'
    png_parts[-2] += '_%d'
    png_name = '.'.join(png_parts)
    command = 'gs -dSAFER -sDEVICE=png16m -dINTERPOLATE -dNumRenderingThreads=8 -r600 -o ' + to_dir + png_name + ' -c 30000000 setvmthreshold -f ' + from_dir + name
    subprocess.call(command, shell=True)

def tesseract_png_to_hocr(from_dir, to_dir, name):
    command = 'tesseract %s %s hocr' % (from_dir + name,
                                        to_dir + name.strip('.png'))
    subprocess.call(command, shell=True)

def done_file(directory, name):
    done_dir = directory + 'done'
    if not os.path.exists(done_dir):
        os.makedirs(done_dir)
    command = 'mv %s %s' % (directory + name, done_dir + '/' + name)
    subprocess.call(command, shell=True)

def process_dir(directory):
    #assumes directory has:
    #/src with pdfs to process, /decrypted, /png, /hocr
    src = directory + '/src/'
    decrypted = directory + '/decrypted/'
    png = directory + '/png/'
    hocr = directory + '/hocr/'

    for f in os.listdir(src):
        print f
        if f == 'done':
            continue
        decrypt_pdf(src, decrypted, f)
        done_file(src, f)

        ghostscript_pdf_to_png(decrypted, png, f)
        done_file(decrypted, f)

        for png_f in os.listdir(png):
            tesseract_png_to_hocr(png, hocr, png_f)
            done_file(png, png_f)


