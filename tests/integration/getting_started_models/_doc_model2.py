# ==================================================
# For documentation
# ==================================================
from .example_model2 import model

import os
from pathlib import Path
HERE = os.path.abspath(os.path.dirname(__file__))
model.get('post_proc').set('plot_settings', {'show': False, 'save': HERE})
r = model.run()

old_fname = Path(r.get('files').get('plots')[0])
new_fname = os.path.join(os.path.dirname(old_fname), 'example_model2.png')
os.rename(old_fname, new_fname)

