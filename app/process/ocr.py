import os
import subprocess

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
    to_dir += '_'.join(name.split('.')[0].split('_')[:-1])
    if not os.path.exists(to_dir):
        os.mkdir(to_dir)
    command = 'tesseract %s %s hocr' % (from_dir + name,
                                        to_dir + '/' + name.split('.png')[0])
    subprocess.call(command, shell=True)

def done_file(directory, name):
    if name == 'done':
        return
    done_dir = directory + 'done'
    if not os.path.exists(done_dir):
        os.makedirs(done_dir)
    command = 'mv %s %s' % (directory + name, done_dir + '/' + name)
    subprocess.call(command, shell=True)
