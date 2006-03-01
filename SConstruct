import os,sys,string,glob
import SCons.Node.FS

def run(command):
    print command
    return os.popen(command).read()

sys.path.insert(0,'..')
import neveredit
version = neveredit.__version__

Ditto = Action('ditto --rsrc -V $SOURCE.abspath $TARGET.abspath')

def build_dmg(target,source,env):
    basename = str(target[0]).split('-')[0]
    out = run("hdiutil mount " + basename + "_build.dmg.sparseimage")
    device = None
    for line in out.split('\n'):
        parts = line.split()
        if len(parts) == 3 and parts[2].find(basename) != -1:
            if device:
                print 'error: several neveredit volumes appear to be mounted'
                return 1
            device = parts[0]
            mountpoint = parts[2]
    if not device:
        print 'error: mounting source image does not seem to work'
        return 1
    print device,'mounted on',mountpoint            
    pwd = os.getcwd()
    print [str(s) for s in source]
    for f in os.listdir(mountpoint):
        if f in [os.path.basename(str(s)) for s in source] or f.endswith('.app') or\
               f == '.Trashes':
            Execute(Delete(os.path.join(mountpoint,f)))
    for s in source:
        f = os.path.join(mountpoint,os.path.basename(str(s)))
        run('ditto --rsrc ' + os.path.join(pwd,str(s)) + ' ' + f)
        if os.path.isfile(f): #assume all files are text
            run("/Developer/Tools/SetFile -t 'TEXT' + f")
    if not run("hdiutil detach " + device).endswith('ejected.\n'):
        print 'error unmounting build disk image'
        return 1    
    out = run("hdiutil convert -ov " + basename + "_build.dmg.sparseimage -format UDZO "
              "-imagekey zlib-level=9 -o " + str(target[0])).split('\n')
    if not out[-2].endswith(str(target[0])):
        print 'error compressing sparse source image'
        print out[-1]
        return 1
    print string.join(out[-5:],'\n')
    return 0

dmg_builder = Builder(action = [Delete('$TARGET'),
                                build_dmg],
                      source_factory = SCons.Node.FS.default_fs.Entry)


sources = glob.glob('*/*.py') + glob.glob('*.png') + ['README','COPYING']
bundle_builder = Builder(action = 'python setup.py py2app $TARGET.filebase',
                         target_factory = Dir,
                         suffix='.app')

env = Environment(ENV = {'PATH':os.environ['PATH']})

env.Append(BUILDERS = {'DiskImage': dmg_builder,
                       'AppBundle': bundle_builder})


neveredit_app = env.AppBundle(target='dist/neveredit',
                              source=sources + ['neveredit.icns'])

neveredit_dmg = env.DiskImage(target='neveredit-' + version + '.dmg',
                              source = ['dist/neveredit.app',
                                        'README',
                                        'COPYING'])

neverscript_app = env.AppBundle(target='dist/neverscript',
                                source=sources + ['neverscript.icns'])

neverscript_dmg = env.DiskImage(target='neverscript-' + version + '.dmg',
                                source = ['dist/neverscript.app',
                                          'README',
                                          'COPYING'])

docs = env.Command('html/index.html',sources,
                   'epydoc --html -n neveredit -o html -u "http://neveredit.sf.net" ./')

change = env.Command('ChangeLog',
                     sources,
                     'cvs2cl -S --no-wrap --accum --tags --prune --ignore Changelog')

env.Alias('docs',[docs])
ud = Alias('upload-docs','html/index.html','rsync -avPz --delete html/ sumpfork@shell.sf.net:/home/groups/n/ne/neveredit/htdocs/apidocs/')
env.AlwaysBuild(ud)

env.Alias('change',[change])
env.Alias('dmgs',[neveredit_dmg,neverscript_dmg])
env.Alias('bundles',[neveredit_app,neverscript_app])

env.Default(['bundles','dmgs'])
