# selection-under-heat
Project examining the evolution of thermotolerance in the photorespiratory pathway

The general outline of this project's workflow is to identify the sequences of photorespiration pathway genes across a wide range of species, in order to apply models to determine sites within those genes that may be under selective pressure for heat tolerance. 

## Data
The data used in this project come from two sources: the genomes in [Phytozome](https://phytozome-next.jgi.doe.gov/), and RNAseq samples from the [Sequence Read Archive](https://www.ncbi.nlm.nih.gov/sra) for a set of species in clades known to exhibit thermotolerance.

The details of how species and samples were chosen from the SRA are detailed in `notebooks/species_wrangling.ipynb`. In short, we started with a manually-curated list of species that are known to be heat tolerant and some that are not, and chose SRA studies, where possible, that contained paired-end reads from leaf tissue. Where not possible, we took what data was available. 

## *de novo* transcriptome assembly
Because our goal was to find the sequences of photorespiration genes only, we used a single replicate to build our reference transcriptomes. We used the [nf-core/denovotranscript pipeline](https://nf-co.re/denovotranscript/1.2.1/) to assemble transcriptomes. The shell script used to run these assemblies is `job_templates/run_assemblies_nf_core.sb`.

An important note for re-running the assemblies is that the pipeline, alrgely due to trinity, produces a very large number of intermediate files. Because we're running tens of assemblies at a time, this becomes a limiting factor quite quickly, as MSU's HPCC has a scratch file number quota of 1 million files. If you need to re-run these assemblies for any reason, you'll either need to request a temporary file cap increase to 5 million in order to run the job script provided as-is; otherwise, you can just lower the number of jobs running at a time by changing the number after the `%` in the `#SBATCH --array=1-57%25` to a lower number; I think 5 should work, but if you get disk quota exceeded errors, lower the number farther.

## Obtaining protein sequences
Because the species are so broadly distributed phylogenetically, we can't just look for the same nucleotide sequences. Instead, we need to get protein sequences for both the Phytozome genomes and the *de novo* transcriptomes.

### Genome translation
For the genomes, we used the [`transeq` tool provided by EMBOSS](https://ebi-biows.gitdocs.ebi.ac.uk/documentation/faqs/transeq/).

To load the module on MSU's HPCC:
```
module load EMBOSS/6.6.0-foss-2023a
```

To translate the zipped genomes, run the following from the directory where you have the genome `.fasta.gz` files stored:
```
for f in *; do
if [[ "${f##*.}" == "gz" ]]; then
gunzip -c ${f} | transeq -sequence stdin -outseq "translated_${f%.*}"
sed '/^>/s/_1//1' "translated_${f%.*}" | gzip > "translated_protein_seqs/translated_${f}"
rm "translated_${f%.*}"
fi
done
```
`transeq` requires the genomes to be unzipped; we don't want to have to permanently make space for unzipped genomes, so the above snippet unzips them and passes the unzipped fastas to the translation code. `transeq` adds an `_1` at the end of each gene ID, which can cause issues downstream, so the `sed` command included above removes that unnecessary suffix before zipping the output and removing the unzipped version.

### Protein sequences from transcriptomes
The `nf-core/denovotranscript` pipeline implements the tool [EvidentialGene](http://arthropods.eugenes.org/EvidentialGene/) for redundancy reduction, which also provides translated protein sequences for the genetic sequences. These redundancy-reduced files are the `evigene/okayset/all_assembled.okay.aa` files included in each output directory; they were all copied to the same directory for downstream use with the following command, run from the top level of the nf-core pipeline output directory:

```
for d in *; do
cp ${d}/evigene/okayset/all_assembled.okay.aa ../orthofinder/${d}_translated_proteins.fa
done
```

## Orthofinder
Finally, to identify the photorespiration genes, we need to run the [Orthofinder tool](https://github.com/OrthoFinder/OrthoFinder) on our obtained protein sequences. As [described in the Orthofinder docs](https://github.com/OrthoFinder/OrthoFinder?tab=readme-ov-file#advanced-usage---scaling-to-thousands-of-species), when running Orthofinder with more more than 100 species, there is a specific implementation designed to make the runs more efficient. This involves a run with a 64-species "base set", followed by a run that adds any additional species to the core run.

As the Orthofinder developers advise making the 64 species base set encompass as much phylogenetic diversity as possible, we randomly selected 64 of the Phytozome genomes to serve as  the base set, and added the rest of the genomes and the transcriptomes in the addition. The job submission scripts used to run these processes are located in `job_templates`.
