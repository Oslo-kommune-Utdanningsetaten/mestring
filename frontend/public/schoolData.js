export const data = {
  "students": [
    {
      "id": "pia-eriksen",
      "name": "Pia Eriksen",
      "age": 10,
      "groupIds": ["4A", "norwegian", "math", "english"],
      "goalIds": ["goal-01", "goal-02", "goal-03"]
    },
    {
      "id": "camilla-hovberg",
      "name": "Camilla Hovberg",
      "age": 10,
      "groupIds": ["4A", "norwegian", "math"],
      "goalIds": []
    },
    {
      "id": "tony-lupin",
      "name": "Tony Lupin",
      "age": 11,
      "groupIds": ["5A", "norwegian"],
      "goalIds": []
    },
    {
      "id": "sara-kahn",
      "name": "Sara Kahn",
      "age": 12,
      "groupIds": ["5A", "norwegian", "math", "english"],
      "goalIds": []
    }
  ],
  "groups": [
    {
      "id": "4A",
      "name": "4A",
      "type": "basis",
      "grade": 4,
      "teacherIds": []
    },
    {
      "id": "5A",
      "name": "5A",
      "type": "basis",
      "grade": 5,
      "teacherIds": ["teacher-01", "teacher-02", "teacher-04"]
    },
    {
      "id": "norwegian",
      "name": "Norsk",
      "type": "teaching",
      "grade": 1,
      "teacherIds": []
    },
    {
      "id": "math",
      "name": "Matte",
      "type": "teaching",
      "grade": 1,
      "teacherIds": []
    },
    {
      "id": "english",
      "name": "Engelsk",
      "type": "teaching",
      "grade": 1,
      "teacherIds": []
    },
    {
      "id": "science",
      "name": "Naturfag",
      "type": "teaching",
      "grade": 1,
      "teacherIds": []
    }
  ],
  "teachers": [
    {
      "id": "teacher-01",
      "name": "Lars Hansen",
    },
    {
      "id": "teacher-02",
      "name": "Maria Kemp",
    },
    {
      "id": "teacher-03",
      "name": "Jens Giovanni",
    },
    {
      "id": "teacher-04",
      "name": "Ilhan Berisha",
    }
  ],
  "goals": [
    {
      "id": "goal-01",
      "title": "Telle til 10",
      "description": "Eleven kan telle til 10.",
      "groupId": "math",
    },
    {
      "id": "goal-02",
      "title": "Kan skrive navnet sitt",
      "description": "Eleven kan skrive navnet sitt med blyant og papir.",
      "groupId": "norwegian",
    },
    {
      "id": "goal-03",
      "title": "Bidrar i samtaler",
      "description": "Eleven birdrar i samtaler med læreren og medelever.",
      "groupId": "4A",
    },
    {
      "id": "goal-04",
      "title": "Vaske hendene",
      "description": "Eleven skal kunne vaske hendene selvstendig.",
      "groupId": "4A",
    },
    {
      "id": "goal-05",
      "title": "Gi uttrykk for behov",
      "description": "Eleven skal kunne gi uttrykk for behov og basale følelser ved bruk av riktige ord.",
      "groupId": "4A",
    }
  ],
  "observations": [
    {
      "id": "obs-pia-01",
      "createdAt": "2024-06-02T14:25:00Z",
      "masteryValue": 35,
      "groupId": "math",
      "goalId": "goal-01",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-02",
      "createdAt": "2025-01-19T09:15:00Z",
      "masteryValue": 44,
      "groupId": "math",
      "goalId": "goal-01",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-03",
      "createdAt": "2024-06-02T10:30:00Z",
      "masteryValue": 5,
      "groupId": "norwegian",
      "goalId": "goal-02",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-04",
      "createdAt": "2025-01-20T13:45:00Z",
      "masteryValue": 38,
      "groupId": "norwegian",
      "goalId": "goal-02",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-05",
      "createdAt": "2024-06-14T13:00:00Z",
      "masteryValue": 58,
      "groupId": "4A",
      "goalId": "goal-03",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-06",
      "createdAt": "2025-01-20T13:45:00Z",
      "masteryValue": 89,
      "groupId": "4A",
      "goalId": "goal-03",
      "studentId": "pia-eriksen"
    }
  ],
  "masteryLevels": [
    {
      "text": "Mestrer ikke",
      "minValue": 0,
      "maxValue": 20,
      "color": "rgb(229, 50, 43)"
    },
    {
      "text": "Mestrer sjelden",
      "minValue": 21,
      "maxValue": 40,
      "color": "rgb(159, 113, 202)"
    },
    {
      "text": "Mestrer i blant",
      "minValue": 41,
      "maxValue": 60,
      "color": "rgb(86, 174, 232)"
    },
    {
      "text": "Mestrer ofte",
      "minValue": 61,
      "maxValue": 80,
      "color": "rgb(241, 249, 97)"
    },
    {
      "text": "Mestrer",
      "minValue": 81,
      "maxValue": 100,
      "color": "rgb(160, 207, 106)"
    }
  ]
}