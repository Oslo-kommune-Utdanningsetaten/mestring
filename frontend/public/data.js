export const data = {
  "students": [
    {
      "id": "pia-eriksen",
      "name": "Pia Eriksen",
      "age": 10,
      "groupIds": ["5A", "norwegian", "math", "english"],
      "goalIds": ["goal-01", "goal-02"]
    },
    {
      "id": "camilla-hovberg",
      "name": "Camilla Hovberg",
      "age": 10,
      "groupIds": ["5A", "norwegian", "math"],
      "goalIds": []
    },
    {
      "id": "tony-lupin",
      "name": "Tony Lupin",
      "age": 9,
      "groupIds": ["3D", "norwegian"],
      "goalIds": []
    },
    {
      "id": "frank-larsen",
      "name": "Frank Larsen",
      "age": 13,
      "groupIds": ["8C", "norwegian", "math", "english"],
      "goalIds": []
    }
  ],
  "groups": [
    {
      "id": "5A",
      "name": "5A",
      "type": "basis",
      "grade": 5,
      "section": "A",
      "teacherId": "teacher-01"
    },
    {
      "id": "3D",
      "name": "3D",
      "type": "basis",
      "grade": 3,
      "section": "D",
      "teacherId": "teacher-02"
    },
    {
      "id": "8C",
      "name": "8C",
      "type": "basis",
      "grade": 8,
      "section": "C",
      "teacherId": "teacher-03"
    },
    {
      "id": "norwegian",
      "name": "Norsk",
      "type": "teaching"
    },
    {
      "id": "math",
      "name": "Matte",
      "type": "teaching"
    },
    {
      "id": "english",
      "name": "Engelsk",
      "type": "teaching"
    }
  ],
  "teachers": [
    {
      "id": "teacher-01",
      "name": "Lars Hansen",
      "groupIds": ["5A"]
    },
    {
      "id": "teacher-02",
      "name": "Maria Olsen",
      "groupIds": ["3D"]
    },
    {
      "id": "teacher-03",
      "name": "Jens Pedersen",
      "groupIds": ["8C"]
    }
  ],
  "goals": [
    {
      "id": "goal-01",
      "title": "Telle til 10",
      "description": "Eleven kan telle til 10.",
      "groupId": "math",
      "studentId": "pia-eriksen",
      "observationIds": ["obs-pia-01", "obs-pia-02"]
    },
    {
      "id": "goal-02",
      "title": "Kan skrive navnet sitt",
      "description": "Eleven kan skrive navnet sitt med blyant og papir.",
      "groupId": "norwegian",
      "studentId": "pia-eriksen",
      "observationIds": ["obs-pia-03", "obs-pia-04"]
    }
  ],
  "observations": [
    {
      "id": "obs-pia-01",
      "createdAt": "2024-06-02T14:25:00+02:00",
      "masteryValue": 35,
      "groupId": "math",
      "goalId": "goal-01",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-02",
      "createdAt": "2025-01-19T09:15:00+01:00",
      "masteryValue": 44,
      "groupId": "math",
      "goalId": "goal-01",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-03",
      "createdAt": "2024-06-02T10:30:00+02:00",
      "masteryValue": 5,
      "groupId": "norwegian",
      "goalId": "goal-02",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-04",
      "createdAt": "2025-01-20T13:45:00+01:00",
      "masteryValue": 38,
      "groupId": "norwegian",
      "goalId": "goal-02",
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