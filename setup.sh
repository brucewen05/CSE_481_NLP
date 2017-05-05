# !/bin/bash

if [ $# != 3 ]
then
    echo "${0} corpus_name config_yaml train_steps"
    exit 1
fi

corpus_name="$1"
train_steps="$3"
data_path="/data"

echo "Using corpus: ${corpus_name}"
echo "Using train steps: ${train_steps}"

vocab_source="${data_path}/vocab/${corpus_name}"
echo "export VOCAB_SOURCE=${vocab_source}"
export VOCAB_SOURCE=${vocab_source}
echo "export VOCAB_TARGET=${vocab_source}"
export VOCAB_TARGET=${vocab_source}

train_sources="${data_path}/train/${corpus_name}.source"
echo "export TRAIN_SOURCES=${train_sources}"
export TRAIN_SOURCES=${train_sources}

train_targets="${data_path}/train/${corpus_name}.target"
echo "export TRAIN_TARGETS=${train_targets}"
export TRAIN_TARGETS=${train_targets}

dev_sources="${data_path}/dev/${corpus_name}.source"
echo "export DEV_SOURCES=${dev_sources}"
export DEV_SOURCES=${dev_sources}

dev_targets="${data_path}/dev/${corpus_name}.target"
echo "export DEV_TARGETS=${dev_targets}"
export DEV_TARGETS=${dev_targets}

echo "export DEV_TARGETS_REF=${dev_targets}"
echo "what is DEV_TARGETS_REF..?"
export DEV_TARGETS_REF=${dev_targets}

echo "export TRAIN_STEPS=${train_steps}"
export TRAIN_STEPS=${train_steps}

echo "export CONFIG_FILE=$2"
export CONFIG_FILE=$2
