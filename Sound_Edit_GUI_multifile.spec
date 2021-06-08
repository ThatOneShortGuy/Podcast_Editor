# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['Sound_Edit_GUI.py'],
             pathex=['D:\\Podcast Data'],
             binaries=[],
             datas=[(r'C:\Users\braxt\AppData\Local\Programs\Python\Python39\Lib\site-packages\librosa\util\example_data', 'librosa\\util\\example_data')],
             hiddenimports=['sklearn.neighbors._quad_tree', 'sklearn','sklearn.neighbors._typedefs', 'sklearn.utils.weight_vector', 'sklearn.utils.lgamma', 'sklearn.utils.sparsetools._graph_tools', 'sklearn.utils.sparsetools._graph_validation', 'scipy._lib.messagestream', 'sklearn.tree', 'sklearn.neighbors.typedefs', 'sklearn.utils._weight_vector', 'sklearn.neighbors.quad_tree', 'sklearn.tree._utils', 'sklearn.utils._cython_blas', 'scipy.special.cython_special'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['pygame', 'IPython'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Sound_Edit_GUI',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               upx_exclude=[],
               name='Sound_Edit_GUI')
