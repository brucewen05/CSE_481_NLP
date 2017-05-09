# !/bin/bash
if [ $# != 3 ]
then
    echo "${0} corpus_name config_yaml train_steps"
    exit 1
fi


# source the setup.sh using the passed-in arguments to this script
source setup.sh
model_dir="/data/model/${1}_`date +%m_%d`"

if [ -d ${model_dir} ]
then
    echo "${model_dir} already exists, are you sure you want to overwrite it? [y/n]"
    read ANS
    if [[ $ANS != [yY]* ]]
    then
	exit
    fi
fi

mkdir -p $model_dir

#echo "$VOCAB_SOURCE"
#echo "$VOCAB_TARGET"
#echo "$TRAIN_SOURCES"
#echo "$TRAIN_TARGETS"
#echo "$DEV_SOURCES"
#echo "$DEV_TARGETS"
#echo "$TRAIN_STEPS"
#echo "$model_dir"

python3 seq2seq/bin/train.py \
	--config_paths="
      ./config_files/$CONFIG_FILE, 
      ./config_files/train_seq2seq.yml" \
	--model_params "
      vocab_source: $VOCAB_SOURCE
      vocab_target: $VOCAB_TARGET" \
	--input_pipeline_train "
    class: ParallelTextInputPipeline
    params:
      source_files:
        - $TRAIN_SOURCES
      target_files:
        - $TRAIN_TARGETS" \
	--input_pipeline_dev "
    class: ParallelTextInputPipeline
    params:
       source_files:
        - $DEV_SOURCES
       target_files:
        - $DEV_TARGETS" \
	--batch_size 32 \
	--train_steps $TRAIN_STEPS \
	--output_dir $model_dir \
	--save_checkpoints_steps 10000 \
	--eval_every_n_steps 10000
