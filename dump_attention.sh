python3 -m bin.infer \
  --tasks "
    - class: DecodeText
    - class: DumpAttention
      params:
        output_dir: predictions/attention" \
  --model_dir /data/model/mixed_abbrs_05_18_multiencoder_fix \
  --input_pipeline "
    class: ParallelTextInputPipeline
    params:
      source_files:
        - data/sample.source" \
  > predictions/predictions.txt
