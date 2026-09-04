"""
Lightweight, robust in-place Jupyter notebook runner.
Executes code cells in sequence, captures stdout, stderr, and matplotlib figures,
and writes updated cell execution outputs back to the .ipynb file.
"""
import io
import json
import base64
import sys
import contextlib
import matplotlib.pyplot as plt
from pathlib import Path


def execute_notebook(notebook_path: str, working_dir: str = None):
    nb_file = Path(notebook_path).resolve()
    print(f"Executing notebook: {nb_file.name}...")
    
    if working_dir:
        cwd = Path(working_dir).resolve()
    else:
        cwd = nb_file.parent

    # Save original directory
    orig_dir = Path.cwd()
    import os
    os.chdir(str(cwd))
    sys.path.insert(0, str(cwd.parent))
    sys.path.insert(0, str(cwd))

    with open(nb_file, "r", encoding="utf-8") as f:
        nb = json.load(f)

    # Shared execution namespace
    exec_globals = {
        "__name__": "__main__",
        "__file__": str(nb_file),
    }

    exec_count = 1
    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "code":
            source_lines = cell.get("source", [])
            if isinstance(source_lines, list):
                source_code = "".join(source_lines)
            else:
                source_code = str(source_lines)

            # Skip empty cells
            if not source_code.strip():
                cell["execution_count"] = None
                cell["outputs"] = []
                continue

            stdout_buf = io.StringIO()
            stderr_buf = io.StringIO()
            cell_outputs = []

            # Capture figures
            plt.close('all')
            
            try:
                with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
                    exec(source_code, exec_globals)
                
                # Check for printed text
                out_text = stdout_buf.getvalue()
                if out_text:
                    cell_outputs.append({
                        "name": "stdout",
                        "output_type": "stream",
                        "text": [out_text if out_text.endswith("\n") else out_text + "\n"]
                    })

                # Check for generated matplotlib figures
                fig_nums = plt.get_fignums()
                for num in fig_nums:
                    fig = plt.figure(num)
                    img_buf = io.BytesIO()
                    fig.savefig(img_buf, format="png", bbox_inches="tight", dpi=150)
                    img_buf.seek(0)
                    img_b64 = base64.b64encode(img_buf.read()).decode("utf-8")
                    cell_outputs.append({
                        "data": {
                            "image/png": img_b64,
                            "text/plain": [f"<Figure size {fig.get_size_inches()[0]*100}x{fig.get_size_inches()[1]*100} with {len(fig.axes)} Axes>"]
                        },
                        "metadata": {},
                        "output_type": "display_data"
                    })
                    plt.close(fig)

                cell["execution_count"] = exec_count
                cell["outputs"] = cell_outputs
                exec_count += 1

            except Exception as e:
                err_msg = f"{type(e).__name__}: {str(e)}"
                print(f"Error executing cell {exec_count}: {err_msg}")
                cell_outputs.append({
                    "ename": type(e).__name__,
                    "evalue": str(e),
                    "output_type": "error",
                    "traceback": [err_msg]
                })
                cell["execution_count"] = exec_count
                cell["outputs"] = cell_outputs
                exec_count += 1

    os.chdir(str(orig_dir))

    # Write back updated notebook
    with open(nb_file, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)

    print(f"Notebook {nb_file.name} successfully executed and saved with updated outputs ({exec_count-1} code cells).")


if __name__ == "__main__":
    target_nb = sys.argv[1] if len(sys.argv) > 1 else "notebooks/01_Surrogate_Predictor.ipynb"
    execute_notebook(target_nb)
