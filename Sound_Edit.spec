# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['Sound_Edit.py'],
             pathex=['G:\\Podcast_Editor'],
             binaries=[],
             datas=[(r'C:\Users\braxt\AppData\Local\Programs\Python\Python39\Lib\site-packages\librosa\util\example_data', 'librosa\\util\\example_data')],
             hiddenimports=['sklearn.neighbors._quad_tree', 'sklearn','sklearn.neighbors._typedefs', 'sklearn.utils.weight_vector', 'sklearn.utils.lgamma', 'sklearn.utils.sparsetools._graph_tools', 'sklearn.utils.sparsetools._graph_validation', 'scipy._lib.messagestream', 'sklearn.tree', 'sklearn.neighbors.typedefs', 'sklearn.utils._weight_vector', 'sklearn.neighbors.quad_tree', 'sklearn.tree._utils', 'sklearn.utils._cython_blas', 'scipy.special.cython_special'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Sound_Edit',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
