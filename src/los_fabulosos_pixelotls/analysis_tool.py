def clasificator_analisis(model, X, y):
  '''Compute accuracy with CV, confusion matrix, precision-recall scores and plot ROC and precision-recall curves.
   Args: 
     model = model object trained from sklearn
         X = input features in train or test
         y = target in train or test
   Return:
    Print of all the scores computed and save accuracy, cm, precision, recall
'''
  
  from sklearn.model_selection import cross_val_predict, cross_val_score
  from sklearn.metrics import confusion_matrix, precision_score, recall_score, plot_precision_recall_curve, plot_roc_curve

  accu = cross_val_score(model, X, y, cv=5, scoring="accuracy").mean()
  print(f'{model} \nAccuracy:{accu}\n')
  pred = cross_val_predict(model, X, y, cv=5)
  cm = confusion_matrix(y,pred)
  print(f'Confusion Matrix: \n {cm}\n')
  precision = precision_score(y,pred)
  print('Precision:',precision)
  recall = recall_score(y, pred)
  print('Recall:', recall)
  plot_precision_recall_curve(model, X, y)
  plt.show()

  plot_roc_curve(model, X, y)
  plt.plot([0, 1], [0, 1], color='0.5', ls=':')
  plt.show()
  
  #return accu, cm, precision, recall
