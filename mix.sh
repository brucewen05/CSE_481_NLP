rm train/mixed*
rm dev/mixed*
rm test/mixed*

cat train/*abbrs.source > train/mixed_abbrs.source
cat dev/*abbrs.source > dev/mixed_abbrs.source
cat test/*abbrs.source > test/mixed_abbrs.source

cat train/*abbrs_words.target > train/mixed_abbrs_words.target
cat dev/*abbrs_words.target > dev/mixed_abbrs_words.target
cat test/*abbrs_words.target > test/mixed_abbrs_words.target

cat train/*abbrs_words.source > train/mixed_abbrs_words.source
cat dev/*abbrs_words.source > dev/mixed_abbrs_words.source
cat test/*abbrs_words.source > test/mixed_abbrs_words.source

cat train/*abbrs.target > train/mixed_abbrs.target
cat dev/*abbrs.target > dev/mixed_abbrs.target
cat test/*abbrs.target > test/mixed_abbrs.target


