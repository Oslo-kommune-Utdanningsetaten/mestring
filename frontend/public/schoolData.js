export const data = {
  "students": [
    {
      "id": "pia-eriksen",
      "name": "Pia Eriksen",
      "age": 10,
      "groupIds": ["5A", "norwegian", "math", "english"],
      "goalIds": ["goal-01", "goal-02", "goal-03"]
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
      "teacherIds": ["teacher-01", "teacher-02", "teacher-04"]
    },
    {
      "id": "3D",
      "name": "3D",
      "type": "basis",
      "grade": 3,
      "section": "D",
      "teacherIds": ["teacher-02"]
    },
    {
      "id": "8C",
      "name": "8C",
      "type": "basis",
      "grade": 8,
      "section": "C",
      "teacherIds": ["teacher-03"]
    },
    {
      "id": "norwegian",
      "name": "Norsk",
      "type": "teaching",
      "teacherIds": ["teacher-02", "teacher-03"]
    },
    {
      "id": "math",
      "name": "Matte",
      "type": "teaching",
      "teacherIds": ["teacher-02", "teacher-04"]
    },
    {
      "id": "english",
      "name": "Engelsk",
      "type": "teaching",
      "teacherIds": ["teacher-02"]
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
      "groupId": "5A",
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
    },
    {
      "id": "obs-pia-05",
      "createdAt": "2024-06-14T13:00:00+02:00",
      "masteryValue": 58,
      "groupId": "5A",
      "goalId": "goal-03",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-06",
      "createdAt": "2025-01-20T13:45:00+01:00",
      "masteryValue": 89,
      "groupId": "5A",
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