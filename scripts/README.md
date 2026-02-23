<h1>EMG In-Report Variant Extractor</h1>

<h2>Script Name</h2>
<p><code>emg_extract.py</code></p>

<h2>Overview</h2>
<p>
This script connects to the <strong>Emedgene genomic analysis platform</strong> (Production instance) and:
</p>

<ol>
    <li>Authenticates using EMG credentials</li>
    <li>Retrieves the gene panel (<code>geneListName</code> and gene list) for a given EMG case</li>
    <li>Retrieves all variants for that case</li>
    <li>Filters variants tagged <code>"in_report"</code> (case-insensitive)</li>
    <li>Identifies overlapping genes between:
        <ul>
            <li>Variant <code>gene_name</code></li>
            <li>Case gene panel</li>
        </ul>
    </li>
    <li>Exports the results to a CSV file</li>
</ol>

<p>The output CSV is saved in:</p>

<pre>output/results.csv</pre>

<p>(one directory above the <code>scripts/</code> folder)</p>

<h2>What the Script Produces</h2>

<table>
    <tr>
        <th>Column Name</th>
        <th>Description</th>
    </tr>
    <tr>
        <td>EMG_Number</td>
        <td>The EMG case ID provided by the user</td>
    </tr>
    <tr>
        <td>geneListName</td>
        <td>Name of the gene panel associated with the case</td>
    </tr>
    <tr>
        <td>overlapping_genes</td>
        <td>Genes shared between the variant and the panel (comma-separated)</td>
    </tr>
    <tr>
        <td>variant_details</td>
        <td>Genomic coordinates and size information</td>
    </tr>
</table>

<h2>Directory Structure Assumed</h2>

<pre>
project/
├── output/
├── scripts/
│    └── emg_extract.py
└── README.html
</pre>

<p>The script must be located inside the <code>scripts/</code> directory.</p>

<h2>User Parameter</h2>

<p>The script requires <strong>one command-line argument</strong>:</p>

<pre>EMG_NUMBER</pre>

<p>Example:</p>

<pre>EMG824233283</pre>

<h2>Environment Variables Required</h2>

<p>Before running the script, set your EMG credentials.</p>

<h3>Mac / Linux</h3>
<pre>
export EMG_USERNAME="your_username"
export EMG_PASSWORD="your_password"
</pre>

<h3>Windows (PowerShell)</h3>
<pre>
setx EMG_USERNAME "your_username"
setx EMG_PASSWORD "your_password"
</pre>

<h2>How to Run</h2>

<p>From inside the <code>scripts/</code> directory:</p>

<pre>
python emg_extract.py EMG824233283
</pre>

<h2>Example Output</h2>

<table>
    <tr>
        <th>EMG_Number</th>
        <th>geneListName</th>
        <th>overlapping_genes</th>
        <th>variant_details</th>
    </tr>
    <tr>
        <td>EMG824233283</td>
        <td>CGL121 - Thoracic Aortic Aneurysm and Dissection (TAAD) Panel - 10/2025</td>
        <td>FLNA, BGN</td>
        <td>chrX:141583737-156010409 14426.67(kb)</td>
    </tr>
    <tr>
        <td>EMG824233283</td>
        <td>CGL121 - Thoracic Aortic Aneurysm and Dissection (TAAD) Panel - 10/2025</td>
        <td>MED12</td>
        <td>chrX:63350069-92387933 29037.86(kb)</td>
    </tr>
</table>

<h2>Behavior Notes</h2>

<ul>
    <li>Tag filtering is <strong>case-insensitive</strong> (<code>in_report</code>, <code>In_Report</code>, etc.)</li>
    <li>Multiple overlapping genes appear in a single cell (comma-separated)</li>
    <li>The script creates the <code>output/</code> directory automatically if it does not exist</li>
    <li>If no qualifying variants are found, the CSV will not contain rows</li>
</ul>

<h2>Dependencies</h2>

<ul>
    <li>Python 3.8+</li>
    <li><code>requests</code></li>
    <li><code>pandas</code></li>
</ul>

<p>Install if needed:</p>

<pre>
pip install requests pandas
</pre>

</body>
</html>
