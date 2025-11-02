/*
4- Lista de tareas con prioridad 
Implemente un contrato que permita a cada usuario manejar su propia lista de tareas 
(ToDoList). 
Cada tarea debe contener:
- Un id autoincremental.
- Un título (string).
- Una prioridad (entero entre 1 y 5).
- Un estado (pendiente, en curso, completada).
- La fecha/hora de creación (timestamp).

Se deben emitir eventos (TaskAdded, TaskUpdated, TaskDeleted, 
TaskStatusChanged) para reflejar las operaciones sobre las tareas. 

 */ 


// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ToDoList {

    address[] users;
    mapping(address=>Task[]) users_tasks;
    mapping(address=>uint[]) users_ids;
    uint next_id;
    
    event TaskCreated(address indexed who, uint indexed id, string indexed title);
    event TaskUpdated(address indexed who, uint indexed taskId, string indexed newTitle);
    event TaskDeleted(address indexed who, uint indexed taskId);
    event TaskStatusChanged(address indexed who, uint indexed taskId, State indexed newState);


    constructor(){
        next_id = 1;
    }

    enum State {
        Pending,
        InProgress,
        Completed
    }
     
     struct Task {
        uint id;
        string title;
        uint8 priority;
        State state;
        uint64 timestamp;
    }    


    function createTask(string memory title, uint8 priority) public {
        require(priority >=1 && priority <= 5, "La prioridad debe estar entre 1 y 5");
        require(bytes(title).length > 0, "Titulo vacio");
        uint id = next_id;
        next_id = next_id + 1;
        Task memory t = Task(id, title, priority, State.Pending, uint64(block.timestamp));
        users_tasks[msg.sender].push(t);
        users_ids[msg.sender].push(id);
        emit TaskCreated(msg.sender, id, title);
    }


    function getAllTasks() public view returns (Task[] memory) {
        return users_tasks[msg.sender];
    }
    
    function getTask(uint taskId) public view returns (uint, string memory, uint8, State, uint64) {
        (uint idx, bool found) = searchTask(taskId);
        require(found, "Task not found");
        Task storage t = users_tasks[msg.sender][idx];
        return (t.id, t.title, t.priority, t.state, t.timestamp);
    }


    function updatePriority(uint taskId, uint8 priority) public {
        (uint idx, bool found) = searchTask(taskId);
        require(found, "Task not found");
        users_tasks[msg.sender][idx].priority = priority;
        emit TaskUpdated(msg.sender, taskId, users_tasks[msg.sender][idx].title);
    }
   

    function updateState(uint taskId, State state) public {
        require(uint(state) <= uint(State.Completed), "Invalid State");
        (uint idx, bool found) = searchTask(taskId);
        require(found, "Task not found");
        users_tasks[msg.sender][idx].state = state;
        emit TaskStatusChanged(msg.sender, taskId, state);
    }

    function updateTitle(uint taskId, string memory title) public {
        (uint idx, bool found) = searchTask(taskId);
        require(found, "Task not found");
        users_tasks[msg.sender][idx].title = title;
        emit TaskUpdated(msg.sender, taskId, title);
    }

    function searchTask(uint taskId) internal view returns (uint, bool) {
        for (uint i=0; i<users_ids[msg.sender].length; i++) {
            if (taskId == users_tasks[msg.sender][i].id) {
                  return (i, true);
            }
        }
        return (0, false);
    }

    function deleteTask(uint taskId) public {
        (uint idx, bool found) = searchTask(taskId);
        require(found, "Task not found");
        uint len = users_tasks[msg.sender].length; 
        users_tasks[msg.sender][idx] = users_tasks[msg.sender][len];
        users_tasks[msg.sender].pop();
        emit TaskDeleted(msg.sender, taskId);
    }


    function getTasksPaginated(uint offset, uint limit) public view returns (Task[] memory) {
        require(offset >= 0, "Offset must be greater than or equal to zero");
        require(limit > 0, "Limit must be greater than zero");
        uint total = users_tasks[msg.sender].length;
        if (offset >= total) {
            return new Task[](0);
        }
        uint fin = offset + limit;
        if (fin > total) {
            fin = total;
        }
        uint size = fin - offset;
        Task[] memory paginatedTasks = new Task[](size);
        for (uint i = 0; i < size; i++) {
            paginatedTasks[i] = users_tasks[msg.sender][offset + i];
        }
        return paginatedTasks;
    }

    function getTasksFilteredByState(State state) public view returns (Task[] memory) {
        //tuve que usar 2 for porque no se puede pushear directamente a una lista
        require(uint(state) <= uint(State.Completed), "Invalid State");
        uint count = 0;
        for (uint i = 0; i < users_tasks[msg.sender].length; i++) {
            if (users_tasks[msg.sender][i].state == state) {
                count++;
            }
        }
        Task[] memory filteredTasks = new Task[](count);
        uint index = 0;
        for (uint i = 0; i < users_tasks[msg.sender].length; i++) {
            if (users_tasks[msg.sender][i].state == state) {
                filteredTasks[index] = users_tasks[msg.sender][i];
                index++;
            }
        }
        return filteredTasks;
    }

    function getTasksFilteredByPriority(uint8 priority) public view returns (Task[] memory) {
        require(priority >=1 && priority <= 5, "La prioridad debe estar entre 1 y 5");
        uint count = 0;
        for (uint i = 0; i < users_tasks[msg.sender].length; i++) {
            if (users_tasks[msg.sender][i].priority == priority) {
                count++;
            }
        }
        Task[] memory filteredTasks = new Task[](count);
        uint index = 0;
        for (uint i = 0; i < users_tasks[msg.sender].length; i++) {
            if (users_tasks[msg.sender][i].priority == priority) {
                filteredTasks[index] = users_tasks[msg.sender][i];
                index++;
            }
        }
        return filteredTasks;
    }
}