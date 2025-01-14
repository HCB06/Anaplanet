import networkx as nx
import matplotlib.pyplot as plt
import cupy as cp
from scipy.spatial import ConvexHull
import seaborn as sns
from matplotlib.animation import ArtistAnimation

def draw_neural_web(W, ax, G, return_objs=False):
    """
    Visualizes a neural web by drawing the neural network structure.

    Parameters:
    W : numpy.ndarray
        A 2D array representing the connection weights of the neural network.
    ax : matplotlib.axes.Axes
        The matplotlib axes where the graph will be drawn.
    G : networkx.Graph
        The NetworkX graph representing the neural network structure.
    return_objs : bool, optional
        If True, returns the drawn objects (nodes and edges). Default is False.

    Returns:
    art1 : matplotlib.collections.PathCollection or None
        Returns the node collection if return_objs is True; otherwise, returns None.
    art2 : matplotlib.collections.LineCollection or None
        Returns the edge collection if return_objs is True; otherwise, returns None.
    art3 : matplotlib.collections.TextCollection or None
        Returns the label collection if return_objs is True; otherwise, returns None.

    Example:
    art1, art2, art3 = draw_neural_web(W, ax, G, return_objs=True)
    plt.show()
    """

    for i in range(W.shape[0]):
        for j in range(W.shape[1]):
            if W[i, j] != 0:
                G.add_edge(f'Output{i}', f'Input{j}', ltpw=W[i, j])

    edges = G.edges(data=True)
    weights = [edata['ltpw'] for _, _, edata in edges]
    pos = {}
    num_motor_neurons = W.shape[0]
    num_sensory_neurons = W.shape[1]

    for j in range(num_sensory_neurons):
        pos[f'Input{j}'] = (0, j)

    motor_y_start = (num_sensory_neurons - num_motor_neurons) / 2
    for i in range(num_motor_neurons):
        pos[f'Output{i}'] = (1, motor_y_start + i) 


    art1 = nx.draw_networkx_nodes(G, pos, ax=ax, node_size=1000, node_color='lightblue')
    art2 = nx.draw_networkx_edges(G, pos, ax=ax, edge_color=weights, edge_cmap=plt.cm.Blues, width=2)
    art3 = nx.draw_networkx_labels(G, pos, ax=ax, font_size=10, font_weight='bold')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.set_title('Neural Web')

    if return_objs == True:

        return art1, art2, art3


def draw_model_architecture(model_name, model_path='', style='basic'):
    """
    Visualizes the architecture of a neural network model.

    Parameters
    ----------
    model_name : str
        The name of the model to be visualized, which will be displayed in the title or label.
    
    model_path : str
        The file path to the model, from which the architecture is loaded. Default is ''
    
    style : str, optional
        The style of the visualization. 
        Options:
            - 'basic': Displays a simplified view of the model architecture.
            - 'detailed': Shows a more comprehensive view, including layer details and parameters.
        Default is 'basic'.
    
    Returns
    -------
    None
        Draws and displays the architecture of the specified model.

        
    Examples
    --------
    >>> draw_model_architecture("MyModel", "path/to/model", style='detailed')
    """
    from .plan_cuda import get_scaler, get_act_pot, get_weights
    from .model_operations_cuda import load_model
    
    model = load_model(model_name=model_name, model_path=model_path)
    
    W = model[get_weights()]
    activation_potentiation = model[get_act_pot()]
    scaler_params = model[get_scaler()]

    text_1 = f"Input Shape:\n{W.shape[1]}"
    text_2 = f"Output Shape:\n{W.shape[0]}"

    if scaler_params is None:
        bottom_left_text = 'Standard Scaler=No'
    else:
        bottom_left_text = 'Standard Scaler=Yes'

    if len(activation_potentiation) != 1 or (len(activation_potentiation) == 1 and activation_potentiation[0] != 'linear'):

        bottom_left_text_1 = f'Aggregation Layers(Aggregates All Conversions)={len(activation_potentiation)}'

    else:

        bottom_left_text_1 = 'Aggregation Layers(Aggregates All Conversions)=0'

    bottom_left_text_2 = 'Potentiation Layer(Fully Connected)=1'

    if scaler_params is None:
        bottom_left_text = 'Standard Scaler=No'
    else:
        bottom_left_text = 'Standard Scaler=Yes'

    num_middle_axes = len(activation_potentiation)

    if style == 'detailed':

        col = 1

    elif style == 'basic':
    
        col = 2

    fig, axes = plt.subplots(1, num_middle_axes + col, figsize=(5 * (num_middle_axes + 2), 5))

    fig.suptitle("Model Architecture", fontsize=16, fontweight='bold')

    for i, activation in enumerate(activation_potentiation):
        x = cp.linspace(-100, 100, 100)
        translated_x_train = draw_activations(x, activation)
        y = translated_x_train

        axes[i].plot(x, y, color='b', markersize=6, linewidth=2, label='Activations Over Depth')
        axes[i].set_title(activation_potentiation[i])

        axes[i].spines['top'].set_visible(False)
        axes[i].spines['right'].set_visible(False)
        axes[i].spines['left'].set_visible(False)
        axes[i].spines['bottom'].set_visible(False)
        axes[i].get_xaxis().set_visible(False)
        axes[i].get_yaxis().set_visible(False)
        

        if i < num_middle_axes - 1:
            axes[i].annotate('', xy=(1.05, 0.5), xytext=(0.95, 0.5), 
                            xycoords='axes fraction', textcoords='axes fraction',
                            arrowprops=dict(arrowstyle="->", color='black', lw=1.5))
    
    if style == 'detailed':
    
        G = nx.Graph()
        draw_neural_web(W=W, ax=axes[num_middle_axes], G=G)

    elif style == 'basic':
    
        circle1 = plt.Circle((0.5, 0.5), 0.4, color='skyblue', ec='black', lw=1.5)
        axes[num_middle_axes].add_patch(circle1)
        axes[num_middle_axes].text(0.5, 0.5, text_1, ha='center', va='center', fontsize=12)
        axes[num_middle_axes].set_xlim(0, 1)
        axes[num_middle_axes].set_ylim(0, 1)
        axes[num_middle_axes].axis('off') 

        circle2 = plt.Circle((0.5, 0.5), 0.4, color='lightcoral', ec='black', lw=1.5)
        axes[-1].add_patch(circle2)
        axes[-1].text(0.5, 0.5, text_2, ha='center', va='center', fontsize=12)
        axes[-1].set_xlim(0, 1)
        axes[-1].set_ylim(0, 1)
        axes[-1].axis('off') 
  
     
    fig.text(0.01, 0, bottom_left_text, ha='left', va='bottom', fontsize=10)
    fig.text(0.01, 0.04, bottom_left_text_1, ha='left', va='bottom', fontsize=10)
    fig.text(0.01, 0.08, bottom_left_text_2, ha='left', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.show()
    
    
def draw_activations(x_train, activation):

    from . import activation_functions_cuda as af

    if activation == 'sigmoid':
        result = af.Sigmoid(x_train)

    elif activation == 'swish':
        result = af.swish(x_train)

    elif activation == 'circular':
        result = af.circular_activation(x_train)

    elif activation == 'mod_circular':
        result = af.modular_circular_activation(x_train)

    elif activation == 'tanh_circular':
        result = af.tanh_circular_activation(x_train)

    elif activation == 'leaky_relu':
        result = af.leaky_relu(x_train)

    elif activation == 'relu':
        result = af.Relu(x_train)

    elif activation == 'softplus':
        result = af.softplus(x_train)

    elif activation == 'elu':
        result = af.elu(x_train)

    elif activation == 'gelu':
        result = af.gelu(x_train)

    elif activation == 'selu':
        result = af.selu(x_train)

    elif activation == 'softmax':
        result = af.Softmax(x_train)

    elif activation == 'tanh':
        result = af.tanh(x_train)

    elif activation == 'sinakt':
        result = af.sinakt(x_train)

    elif activation == 'p_squared':
        result = af.p_squared(x_train)

    elif activation == 'sglu':
        result = af.sglu(x_train, alpha=1.0)

    elif activation == 'dlrelu':
        result = af.dlrelu(x_train)

    elif activation == 'exsig':
        result = af.exsig(x_train)

    elif activation == 'sin_plus':
        result = af.sin_plus(x_train)

    elif activation == 'acos':
        result = af.acos(x_train, alpha=1.0, beta=0.0)

    elif activation == 'gla':
        result = af.gla(x_train, alpha=1.0, mu=0.0)

    elif activation == 'srelu':
        result = af.srelu(x_train)

    elif activation == 'qelu':
        result = af.qelu(x_train)

    elif activation == 'isra':
        result = af.isra(x_train)

    elif activation == 'waveakt':
        result = af.waveakt(x_train)

    elif activation == 'arctan':
        result = af.arctan(x_train)

    elif activation == 'bent_identity':
        result = af.bent_identity(x_train)

    elif activation == 'sech':
        result = af.sech(x_train)

    elif activation == 'softsign':
        result = af.softsign(x_train)

    elif activation == 'pwl':
        result = af.pwl(x_train)

    elif activation == 'cubic':
        result = af.cubic(x_train)

    elif activation == 'gaussian':
        result = af.gaussian(x_train)

    elif activation == 'sine':
        result = af.sine(x_train)

    elif activation == 'tanh_square':
        result = af.tanh_square(x_train)

    elif activation == 'mod_sigmoid':
        result = af.mod_sigmoid(x_train)

    elif activation == 'linear':
        result = x_train

    elif activation == 'quartic':
        result = af.quartic(x_train)

    elif activation == 'square_quartic':
        result = af.square_quartic(x_train)

    elif activation == 'cubic_quadratic':
        result = af.cubic_quadratic(x_train)

    elif activation == 'exp_cubic':
        result = af.exp_cubic(x_train)

    elif activation == 'sine_square':
        result = af.sine_square(x_train)

    elif activation == 'logarithmic':
        result = af.logarithmic(x_train)

    elif activation == 'scaled_cubic':
        result = af.scaled_cubic(x_train, 1.0)

    elif activation == 'sine_offset':
        result = af.sine_offset(x_train, 1.0)

    elif activation == 'spiral':
        result = af.spiral_activation(x_train)

    return result


def plot_evaluate(x_test, y_test, y_preds, acc_list, W, activation_potentiation):
    
    from .metrics_cuda import metrics, confusion_matrix, roc_curve
    from .ui import loading_bars, initialize_loading_bar
    from .data_operations_cuda import decode_one_hot
    from .model_operations_cuda import predict_model_ram
    
    bar_format_normal = loading_bars()[0]
    
    acc = acc_list[len(acc_list) - 1]
    y_true = decode_one_hot(y_test)

    y_true = cp.array(y_true)
    y_preds = cp.array(y_preds)
    Class = cp.unique(decode_one_hot(y_test))

    precision, recall, f1 = metrics(y_test, y_preds)
    
    
    cm = confusion_matrix(y_true, y_preds, len(Class))
    fig, axs = plt.subplots(2, 2, figsize=(16, 12))

    sns.heatmap(cm, annot=True, fmt='d', ax=axs[0, 0])
    axs[0, 0].set_title("Confusion Matrix")
    axs[0, 0].set_xlabel("Predicted Class")
    axs[0, 0].set_ylabel("Actual Class")
    
    if len(Class) == 2:
        fpr, tpr, thresholds = roc_curve(y_true, y_preds)
   
        roc_auc = cp.trapz(tpr, fpr)
        axs[1, 0].plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
        axs[1, 0].plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        axs[1, 0].set_xlim([0.0, 1.0])
        axs[1, 0].set_ylim([0.0, 1.05])
        axs[1, 0].set_xlabel('False Positive Rate')
        axs[1, 0].set_ylabel('True Positive Rate')
        axs[1, 0].set_title('Receiver Operating Characteristic (ROC) Curve')
        axs[1, 0].legend(loc="lower right")
        axs[1, 0].legend(loc="lower right")
    else:

        for i in range(len(Class)):
            
            y_true_copy = cp.copy(y_true)
            y_preds_copy = cp.copy(y_preds)
        
            y_true_copy[y_true_copy == i] = 0
            y_true_copy[y_true_copy != 0] = 1
            
            y_preds_copy[y_preds_copy == i] = 0
            y_preds_copy[y_preds_copy != 0] = 1
            

            fpr, tpr, thresholds = roc_curve(y_true_copy, y_preds_copy)
            
            roc_auc = cp.trapz(tpr, fpr)
            axs[1, 0].plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
            axs[1, 0].plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
            axs[1, 0].set_xlim([0.0, 1.0])
            axs[1, 0].set_ylim([0.0, 1.05])
            axs[1, 0].set_xlabel('False Positive Rate')
            axs[1, 0].set_ylabel('True Positive Rate')
            axs[1, 0].set_title('Receiver Operating Characteristic (ROC) Curve')
            axs[1, 0].legend(loc="lower right")
            axs[1, 0].legend(loc="lower right")
    

    metric = ['Precision', 'Recall', 'F1 Score', 'Accuracy']
    values = [precision, recall, f1, acc]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    
    bars = axs[0, 1].bar(metric, values, color=colors)
    
    
    for bar, value in zip(bars, values):
        axs[0, 1].text(bar.get_x() + bar.get_width() / 2, bar.get_height() - 0.05, f'{value:.2f}',
                       ha='center', va='bottom', fontsize=12, color='white', weight='bold')
    
    axs[0, 1].set_ylim(0, 1) 
    axs[0, 1].set_xlabel('Metrics')
    axs[0, 1].set_ylabel('Score')
    axs[0, 1].set_title('Precision, Recall, F1 Score, and Accuracy (Weighted)')
    axs[0, 1].grid(True, axis='y', linestyle='--', alpha=0.7)
    
    feature_indices=[0, 1]

    h = .02
    x_min, x_max = x_test[:, feature_indices[0]].min() - 1, x_test[:, feature_indices[0]].max() + 1
    y_min, y_max = x_test[:, feature_indices[1]].min() - 1, x_test[:, feature_indices[1]].max() + 1
    xx, yy = cp.meshgrid(cp.arange(x_min, x_max, h),
                         cp.arange(y_min, y_max, h))
    
    grid = cp.c_[xx.ravel(), yy.ravel()]

    try:

        grid_full = cp.zeros((grid.shape[0], x_test.shape[1]))
        grid_full[:, feature_indices] = grid
        
        Z = [None] * len(grid_full)

        predict_progress = initialize_loading_bar(total=len(grid_full),leave=False,
            bar_format=bar_format_normal ,desc="Predicts For Decision Boundary",ncols= 65)

        for i in range(len(grid_full)):

            Z[i] = cp.argmax(predict_model_ram(grid_full[i], W=W, activation_potentiation=activation_potentiation))
            predict_progress.update(1)

        predict_progress.close()

        Z = cp.array(Z)
        Z = Z.reshape(xx.shape)

        axs[1,1].contourf(xx, yy, Z, alpha=0.8)
        axs[1,1].scatter(x_test[:, feature_indices[0]], x_test[:, feature_indices[1]], c=decode_one_hot(y_test), edgecolors='k', marker='o', s=20, alpha=0.9)
        axs[1,1].set_xlabel(f'Feature {0 + 1}')
        axs[1,1].set_ylabel(f'Feature {1 + 1}')
        axs[1,1].set_title('Decision Boundary')

    except Exception as e:
        # Hata meydana geldiğinde yapılacak işlemler
        print(f"Hata oluştu: {e}")

    plt.show()


def plot_decision_boundary(x, y, activation_potentiation, W, artist=None, ax=None):
    
    from .model_operations_cuda import predict_model_ram
    from .data_operations_cuda import decode_one_hot
    
    feature_indices = [0, 1]

    h = .02
    x_min, x_max = x[:, feature_indices[0]].min() - 1, x[:, feature_indices[0]].max() + 1
    y_min, y_max = x[:, feature_indices[1]].min() - 1, x[:, feature_indices[1]].max() + 1
    xx, yy = cp.meshgrid(cp.arange(x_min, x_max, h),
                         cp.arange(y_min, y_max, h))
    
    grid = cp.c_[xx.ravel(), yy.ravel()]
    grid_full = cp.zeros((grid.shape[0], x.shape[1]))
    grid_full[:, feature_indices] = grid
    
    Z = [None] * len(grid_full)

    for i in range(len(grid_full)):
        Z[i] = cp.argmax(predict_model_ram(grid_full[i], W=W, activation_potentiation=activation_potentiation))

    Z = cp.array(Z)
    Z = Z.reshape(xx.shape)

    if ax is None:

        plt.contourf(xx, yy, Z, alpha=0.8)
        plt.scatter(x[:, feature_indices[0]], x[:, feature_indices[1]], c=decode_one_hot(y), edgecolors='k', marker='o', s=20, alpha=0.9)
        plt.xlabel(f'Feature {0 + 1}')
        plt.ylabel(f'Feature {1 + 1}')
        plt.title('Decision Boundary')

        plt.show()

    else:

        try:
            art1_1 = ax[1, 0].contourf(xx, yy, Z, alpha=0.8)
            art1_2 = ax[1, 0].scatter(x[:, feature_indices[0]], x[:, feature_indices[1]], c=decode_one_hot(y), edgecolors='k', marker='o', s=20, alpha=0.9)
            ax[1, 0].set_xlabel(f'Feature {0 + 1}')
            ax[1, 0].set_ylabel(f'Feature {1 + 1}')
            ax[1, 0].set_title('Decision Boundary')

            return art1_1, art1_2
        
        except:

            art1_1 = ax[0].contourf(xx, yy, Z, alpha=0.8)
            art1_2 = ax[0].scatter(x[:, feature_indices[0]], x[:, feature_indices[1]], c=decode_one_hot(y), edgecolors='k', marker='o', s=20, alpha=0.9)
            ax[0].set_xlabel(f'Feature {0 + 1}')
            ax[0].set_ylabel(f'Feature {1 + 1}')
            ax[0].set_title('Decision Boundary')


            return art1_1, art1_2
  
        
def plot_decision_space(x, y, y_preds=None, s=100, color='tab20'):
    
    from .metrics_cuda import pca
    from .data_operations_cuda import decode_one_hot
    
    if x.shape[1] > 2:

        X_pca = pca(x, n_components=2)
    else:
        X_pca = x

    if y_preds == None:
        y_preds = decode_one_hot(y)

    y = decode_one_hot(y)
    num_classes = len(cp.unique(y))
    
    cmap = plt.get_cmap(color)


    norm = plt.Normalize(vmin=0, vmax=num_classes - 1)
    

    plt.scatter(X_pca[:, 0], X_pca[:, 1], c=y, edgecolor='k', s=50, cmap=cmap, norm=norm)
    

    for cls in range(num_classes):

        class_points = []


        for i in range(len(y)):
            if y_preds[i] == cls:
                class_points.append(X_pca[i])
        
        class_points = cp.array(class_points)
        

        if len(class_points) > 2:
            hull = ConvexHull(class_points)
            hull_points = class_points[hull.vertices]

            hull_points = cp.vstack([hull_points, hull_points[0]])
            
            plt.fill(hull_points[:, 0], hull_points[:, 1], color=cmap(norm(cls)), alpha=0.3, edgecolor='k', label=f'Class {cls} Hull')

    plt.title("Decision Space (Data Distribution)")

    plt.draw()
    
        
def neuron_history(LTPW, ax1, row, col, class_count, artist5, data, fig1, acc=False, loss=False):

    for j in range(len(class_count)):
        
            if acc != False and loss != False:
                suptitle_info = data + ' Accuracy:' + str(acc) + '\n' + data + ' Loss:' + str(loss) + '\nNeurons Memory:'
            else:
                suptitle_info = 'Neurons Memory:'

            mat = LTPW[j,:].reshape(row, col)

            title_info = f'{j+1}. Neuron'
            
            art5 = ax1[j].imshow(mat.get(), interpolation='sinc', cmap='viridis')

            ax1[j].set_aspect('equal')
            ax1[j].set_xticks([])
            ax1[j].set_yticks([])
            ax1[j].set_title(title_info)

           
            artist5.append([art5])

    fig1.suptitle(suptitle_info, fontsize=16)

    return artist5


def initialize_visualization_for_fit(val, show_training, neurons_history, x_train, y_train):
    """Initializes the visualization setup based on the parameters."""
    from .data_operations import find_closest_factors
    visualization_objects = {}

    if show_training:
        if not val:
            raise ValueError("For showing training, 'val' parameter must be True.")

        G = nx.Graph()
        fig, ax = plt.subplots(2, 2)
        fig.suptitle('Train History')
        visualization_objects.update({
            'G': G,
            'fig': fig,
            'ax': ax,
            'artist1': [],
            'artist2': [],
            'artist3': [],
            'artist4': []
        })

    if neurons_history:
        row, col = find_closest_factors(len(x_train[0]))
        fig1, ax1 = plt.subplots(1, len(set(y_train)), figsize=(18, 14))
        visualization_objects.update({
            'fig1': fig1,
            'ax1': ax1,
            'artist5': [],
            'row': row,
            'col': col
        })

    return visualization_objects


def update_weight_visualization_for_fit(ax, LTPW, artist2):
    """Updates the weight visualization plot."""
    art2 = ax.imshow(LTPW, interpolation='sinc', cmap='viridis')
    artist2.append([art2])


def update_decision_boundary_for_fit(ax, x_val, y_val, activation_potentiation, LTPW, artist1):
    """Updates the decision boundary visualization."""
    art1_1, art1_2 = plot_decision_boundary(x_val, y_val, activation_potentiation, LTPW, artist=artist1, ax=ax)
    artist1.append([*art1_1.collections, art1_2])


def update_validation_history_for_fit(ax, val_list, artist3):
    """Updates the validation accuracy history plot."""
    period = list(range(1, len(val_list) + 1))
    art3 = ax.plot(
        period, 
        val_list, 
        linestyle='--', 
        color='g', 
        marker='o', 
        markersize=6, 
        linewidth=2, 
        label='Validation Accuracy'
    )
    ax.set_title('Validation History')
    ax.set_xlabel('Time')
    ax.set_ylabel('Validation Accuracy')
    ax.set_ylim([0, 1])
    artist3.append(art3)


def display_visualization_for_fit(fig, artist_list, interval):
    """Displays the animation for the given artist list."""
    ani = ArtistAnimation(fig, artist_list, interval=interval, blit=True)
    plt.tight_layout()
    plt.show()



def initialize_visualization_for_learner(show_history, neurons_history, neural_web_history, x_train, y_train):
    """Initialize all visualization components"""
    from .data_operations import find_closest_factors
    viz_objects = {}
    
    if show_history:
        fig, ax = plt.subplots(3, 1, figsize=(6, 8))
        fig.suptitle('Learner History')
        viz_objects['history'] = {
            'fig': fig,
            'ax': ax,
            'artist1': [],
            'artist2': [],
            'artist3': []
        }
    
    if neurons_history:
        row, col = find_closest_factors(len(x_train[0]))
        if row != 0:
            fig1, ax1 = plt.subplots(1, len(y_train[0]), figsize=(18, 14))
        else:
            fig1, ax1 = plt.subplots(1, 1, figsize=(18, 14))
        viz_objects['neurons'] = {
            'fig': fig1,
            'ax': ax1,
            'artists': [],
            'row': row,
            'col': col
        }
    
    if neural_web_history:
        G = nx.Graph()
        fig2, ax2 = plt.subplots(figsize=(18, 4))
        viz_objects['web'] = {
            'fig': fig2,
            'ax': ax2,
            'G': G,
            'artists': []
        }
    
    return viz_objects

def update_history_plots_for_learner(viz_objects, depth_list, loss_list, best_acc_per_depth_list, x_train, final_activations):
    """Update history visualization plots"""
    if 'history' not in viz_objects:
        return
    
    hist = viz_objects['history']
    
    # Loss plot
    art1 = hist['ax'][0].plot(depth_list, loss_list, color='r', markersize=6, linewidth=2)
    hist['ax'][0].set_title('Test Loss Over Depth')
    hist['artist1'].append(art1)
    
    # Accuracy plot
    art2 = hist['ax'][1].plot(depth_list, best_acc_per_depth_list, color='g', markersize=6, linewidth=2)
    hist['ax'][1].set_title('Test Accuracy Over Depth')
    hist['artist2'].append(art2)
    
    # Activation shape plot
    x = cp.linspace(cp.min(x_train), cp.max(x_train), len(x_train))
    translated_x_train = cp.copy(x)
    for activation in final_activations:
        translated_x_train += draw_activations(x, activation)
    
    art3 = hist['ax'][2].plot(x, translated_x_train, color='b', markersize=6, linewidth=2)
    hist['ax'][2].set_title('Potentiation Shape Over Depth')
    hist['artist3'].append(art3)

def display_visualizations_for_learner(viz_objects, best_weights, data, best_acc, test_loss, y_train, interval):
    """Display all final visualizations"""
    if 'history' in viz_objects:
        hist = viz_objects['history']
        for _ in range(30):
            hist['artist1'].append(hist['artist1'][-1])
            hist['artist2'].append(hist['artist2'][-1])
            hist['artist3'].append(hist['artist3'][-1])
        
        ani1 = ArtistAnimation(hist['fig'], hist['artist1'], interval=interval, blit=True)
        ani2 = ArtistAnimation(hist['fig'], hist['artist2'], interval=interval, blit=True)
        ani3 = ArtistAnimation(hist['fig'], hist['artist3'], interval=interval, blit=True)
        plt.tight_layout()
        plt.show()
    
    if 'neurons' in viz_objects:
        neurons = viz_objects['neurons']
        for _ in range(10):
            neurons['artists'] = neuron_history(
                cp.copy(best_weights), 
                neurons['ax'],
                neurons['row'],
                neurons['col'],
                y_train[0],
                neurons['artists'],
                data=data,
                fig1=neurons['fig'],
                acc=best_acc,
                loss=test_loss
            )
        
        ani4 = ArtistAnimation(neurons['fig'], neurons['artists'], interval=interval, blit=True)
        plt.tight_layout()
        plt.show()
    
    if 'web' in viz_objects:
        web = viz_objects['web']
        for _ in range(30):
            art5_1, art5_2, art5_3 = draw_neural_web(
                W=best_weights,
                ax=web['ax'],
                G=web['G'],
                return_objs=True
            )
            art5_list = [art5_1] + [art5_2] + list(art5_3.values())
            web['artists'].append(art5_list)
        
        ani5 = ArtistAnimation(web['fig'], web['artists'], interval=interval, blit=True)
        plt.tight_layout()
        plt.show()