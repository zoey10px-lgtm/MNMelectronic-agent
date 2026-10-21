"""Compatibility entry point for the supplied augmented training dataset."""
from train_augmented import main
if __name__=='__main__':
 main()
 from finalize_retraining import main as finalize
 finalize()
