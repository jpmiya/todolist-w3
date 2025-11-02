# Juan Pablo Miyagusuku
# Legajo 21549/3


#ADDRESS CONTRATO= 0xc6C40378e74b706F9aE83E8a5909D2Ce08dfA8b2
#etherscan = https://sepolia.etherscan.io/tx/0x14ae9e5911eea551aa1ca422e69c9537fd2a7fae863fa6ecf40d57f20f42ba74

# 4- Lista de Tareas con Prioridad 
#Requerimientos: 
#a) Leer: obtener todas las tareas o filtrarlas por prioridad o estado. 
#b) Escribir: agregar, actualizar o eliminar tareas. 
#c) Escuchar eventos de tareas (TaskAdded, TaskUpdated, TaskDeleted, 
#TaskStatusChanged). 
#d) Implementar la consulta paginada con parámetros offset y limit. 
import utils


state_dict = {
    0: "Pending",
    1: "InProgress",
    2: "Completed"
}

state_dict_rev = {v: k for k, v in state_dict.items()} #para cuando mando un estado como string, al contrato hay que mandarselo como un entero

def getAllTasks():
    return utils.c.functions.getAllTasks().call({"from": utils.ACCOUNT_ADDRESS}) #este from es porque sino el contrato no sabe desde que address se llama

def createTask(title, priority):
    return utils.send_tx(utils.c.functions.createTask(title, priority))


def getTasksFilteredByPriority(priority):
    return utils.c.functions.getTasksFilteredByPriority(priority).call({"from": utils.ACCOUNT_ADDRESS})

def getTasksFilteredByState(state):
    return utils.c.functions.getTasksFilteredByState(state).call({"from": utils.ACCOUNT_ADDRESS})

def updateTitle(id, title):
    return utils.send_tx(utils.c.functions.updateTitle(id, title))

def updateState(id, state):
    return utils.send_tx(utils.c.functions.updateState(id, state_dict_rev[state]))

def updatePriority(id, priority):
    return utils.send_tx(utils.c.functions.updatePriority(id, priority))

def deleteTask(id):
    return utils.send_tx(utils.c.functions.deleteTask(id))

def getTasksPaginated(offset, limit):
    return utils.c.functions.getTasksPaginated(offset, limit).call({"from": utils.ACCOUNT_ADDRESS})


def main():
    assert utils.w3.is_connected(), "No se pudo conectar al nodo Ethereum"
    print("--- zona create ---")
    rcpt = createTask("Comprar leche", 2)
    utils.print_event(rcpt, "TaskCreated")
    rcpt = createTask("Lavar el auto", 1)
    utils.print_event(rcpt, "TaskCreated")
    rcpt = createTask("Hacer ejercicio", 3)
    utils.print_event(rcpt, "TaskCreated")
    tasks = getAllTasks()

    for t in tasks:
       print(f"Tarea ID: {t[0]}, Título: {t[1]}, Prioridad: {t[2]}, Estado: {state_dict[t[3]]}")
    
    print("--- zona update ---")
    rcpt = updateTitle(2, "Comprar pan")
    utils.print_event(rcpt,"TaskUpdated")
    rcpt = updateState(1, "Completed")
    utils.print_event(rcpt,"TaskStatusChanged")
    

    rcpt = updatePriority(3, 1)
    utils.print_event(rcpt,"TaskUpdated")

    tasks = getAllTasks()
    for t in tasks:
       print(f"Tarea ID: {t[0]}, Título: {t[1]}, Prioridad: {t[2]}, Estado: {state_dict[t[3]]}")

    print("--- zona filtros ---")
    print("Filtrado por prioridad 1:")
    tasks = getTasksFilteredByPriority(1)
    for t in tasks:
         print(f"Tarea ID: {t[0]}, Título: {t[1]}, Prioridad: {t[2]}, Estado: {state_dict[t[3]]}")
    print("Filtrado por estado Completed:")
    tasks = getTasksFilteredByState(state_dict_rev["Completed"])
    for t in tasks:
         print(f"Tarea ID: {t[0]}, Título: {t[1]}, Prioridad: {t[2]}, Estado: {state_dict[t[3]]}")
    print("--- zona paginacion ---")
    tasks = getTasksPaginated(0, 2)
    for t in tasks:
         print(f"Tarea ID: {t[0]}, Título: {t[1]}, Prioridad: {t[2]}, Estado: {state_dict[t[3]]}")


if __name__ == "__main__":
    main()