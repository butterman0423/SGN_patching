# !usr/bin/bash

PWD=$(pwd)
DSET=cifar100
CP_INTERVAL=10
EPOCHS=300
DATA_DIR=$PWD/data/$DSET
OUT_DIR=$PWD/out/$DSET
CACHE_DIR=$PWD/.cache/$DSET

SGN_DIR=$1

if [ ! -d $DATA_DIR ]; then
	mkdir $DATA_DIR
fi

if [ ! -d $OUT_DIR ]; then
	mkdir $OUT_DIR
fi

if [ ! -d $CACHE_DIR ]; then
	mkdir $CACHE_DIR
fi


cd $SGN_DIR
source .venv/bin/activate

2>&1
echo "============== RUNNING $DSET TESTS ================"
echo

echo "============== NO NOISE ================"
TEST_NAME=no_noise

if [ ! -f $CACHE_DIR/$TEST_NAME ]; then
	python src/cifar/sgn.py --data_dir=$DATA_DIR \
        	                --output_dir=$OUT_DIR/$TEST_NAME \
                	        --dataset cifar100 \
				--train_epochs=$EPOCHS \
                        	--checkpoint_interval=$CP_INTERVAL

	if [ -z $? ]; then
		touch $CACHE_DIR/$TEST_NAME
	fi
else
	echo "TEST CACHE FOUND, SKIPPING"
fi


echo "============== SYM 20% ================"
echo
TEST_NAME=sym20

if [ ! -f $CACHE_DIR/$TEST_NAME ]; then
	python src/cifar/sgn.py --data_dir=$DATA_DIR \
        	                --output_dir=$OUT_DIR/$TEST_NAME \
                	        --dataset cifar100 \
				--noisy_labels \
				--corruption_type sym \
				--severity 0.2 \
				--train_epochs=$EPOCHS \
                        	--checkpoint_interval=$CP_INTERVAL

	if [ -z $? ]; then
		touch $CACHE_DIR/$TEST_NAME
	fi
else
	echo "TEST CACHE FOUND, SKIPPING"
fi

echo "============== SYM 40% ================"
echo
TEST_NAME=sym40

if [ ! -f $CACHE_DIR/$TEST_NAME ]; then
	python src/cifar/sgn.py --data_dir=$DATA_DIR \
				--output_dir=$OUT_DIR/$TEST_NAME \
                	        --dataset cifar100 \
				--noisy_labels \
				--corruption_type sym \
				--severity 0.4 \
				--train_epochs=$EPOCHS \
                        	--checkpoint_interval=$CP_INTERVAL
	
	if [ -z $? ]; then
		touch $CACHE_DIR/$TEST_NAME
	fi
else
	echo "TEST CACHE FOUND, SKIPPING"
fi

echo "============== SYM 60% ================"
echo
TEST_NAME=sym60

if [ ! -f $CACHE_DIR/$TEST_NAME ]; then
	python src/cifar/sgn.py --data_dir=$DATA_DIR \
        	                --output_dir=$OUT_DIR/$TEST_NAME \
                	        --dataset cifar100 \
				--noisy_labels \
				--corruption_type sym \
				--severity 0.6 \
				--train_epochs=$EPOCHS \
                        	--checkpoint_interval=$CP_INTERVAL

	if [ -z $? ]; then
		touch $CACHE_DIR/$TEST_NAME
	fi
else
	echo "TEST CACHE FOUND, SKIPPING"
fi

echo "============== ASYM 20% ================"
echo
TEST_NAME=asym20

if [ ! -f $CACHE_DIR/$TEST_NAME ]; then
	python src/cifar/sgn.py --data_dir=$DATA_DIR \
        	                --output_dir=$OUT_DIR/$TEST_NAME \
                	        --dataset cifar100 \
				--noisy_labels \
				--corruption_type asym \
				--severity 0.2 \
				--train_epochs=$EPOCHS \
                        	--checkpoint_interval=$CP_INTERVAL

	if [ -z $? ]; then
		touch $CACHE_DIR/$TEST_NAME
	fi
else
	echo "TEST CACHE FOUND, SKIPPING"
fi

echo "============== ASYM 40% ================"
echo
TEST_NAME=asym40

if [ ! -f $CACHE_DIR/$TEST_NAME ]; then
	python src/cifar/sgn.py --data_dir=$DATA_DIR \
        	                --output_dir=$OUT_DIR/$TEST_NAME \
                	        --dataset cifar100 \
				--noisy_labels \
				--corruption_type asym \
				--severity 0.4 \
				--train_epochs=$EPOCHS \
                        	--checkpoint_interval=$CP_INTERVAL

	if [ -z $? ]; then
		touch $CACHE_DIR/$TEST_NAME
	fi
else
	echo "TEST CACHE FOUND, SKIPPING"
fi

echo "============== ASYM 60% ================"
echo
TEST_NAME=asym60

if [ ! -f $CACHE_DIR/$TEST_NAME ]; then
	python src/cifar/sgn.py --data_dir=$DATA_DIR \
        	                --output_dir=$OUT_DIR/$TEST_NAME \
                	        --dataset cifar100 \
				--noisy_labels \
				--corruption_type asym \
				--severity 0.6 \
				--train_epochs=$EPOCHS \
                        	--checkpoint_interval=$CP_INTERVAL

	if [ -z $? ]; then
		touch $CACHE_DIR/$TEST_NAME
	fi
else
	echo "TEST CACHE FOUND, SKIPPING"
fi

