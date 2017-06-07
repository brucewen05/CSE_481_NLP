# !/bin/bash

if [ $# != 4 ]
then
    echo "${0} corpus_name config_yaml train_steps sub_dir_name"
    exit 1
fi

corpus_name="$1"
train_steps="$3"
sub_dir="${4}"
data_path="/data"
vocab_source="${data_path}/vocab/wiki"
vocab_target="${data_path}/vocab/wiki"
#vocab_target="${data_path}/vocab/words_small"

echo "Using corpus: ${corpus_name}"
echo "Using train steps: ${train_steps}"

echo "export VOCAB_SOURCE=${vocab_source}"
export VOCAB_SOURCE=${vocab_source}
echo "export VOCAB_TARGET=${vocab_source}"
export VOCAB_TARGET=${vocab_target}

train_sources="${data_path}/train/${sub_dir}/${corpus_name}.source"
echo "export TRAIN_SOURCES=${train_sources}"
export TRAIN_SOURCES=${train_sources}

train_targets="${data_path}/train/${sub_dir}/${corpus_name}.target"
echo "export TRAIN_TARGETS=${train_targets}"
export TRAIN_TARGETS=${train_targets}

dev_sources="${data_path}/dev/${sub_dir}/${corpus_name}.source"
echo "export DEV_SOURCES=${dev_sources}"
export DEV_SOURCES=${dev_sources}

dev_targets="${data_path}/dev/${sub_dir}/${corpus_name}.target"
echo "export DEV_TARGETS=${dev_targets}"
export DEV_TARGETS=${dev_targets}

echo "export DEV_TARGETS_REF=${dev_targets}"
echo "what is DEV_TARGETS_REF..?"
export DEV_TARGETS_REF=${dev_targets}

echo "export TRAIN_STEPS=${train_steps}"
export TRAIN_STEPS=${train_steps}

echo "export CONFIG_FILE=$2"
export CONFIG_FILE=$2
