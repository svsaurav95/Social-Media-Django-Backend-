# Social Media API

**Social Media API** is a robust platform built using Django and Django REST Framework (DRF). It allows users to interact in a social media-like environment, supporting features such as **creating posts**, **following/unfollowing users**, **managing user actions (hide/block)**, and **generating personalized feeds**. The platform is secured with JWT authentication and provides a seamless API interface for interaction.

<br>

### Table of Contents

- [Features](#features)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Installation](#installation)
- [License](#license)

---

### Features

1. **User Authentication**: Secure authentication using JWT.
2. **Create Posts**: Users can create, view, and manage posts.
3. **Follow/Unfollow Users**: Enables users to follow or unfollow others.
4. **Hide/Block Users**: Allows managing visibility of content through hide/block actions.
5. **Personalized Feed**: Generates a custom feed for users based on their preferences.

---

### Usage

1. Authenticate and obtain a JWT token.
2. Use the token to access API endpoints for creating posts, following/unfollowing users, and managing actions.
3. Retrieve a personalized feed based on your network and preferences.

---

### API Endpoints

Below are some of the key endpoints provided by the API:

#### Authentication
- `POST /api/token/`: Obtain JWT token.
- `POST /api/token/refresh/`: Refresh JWT token.

#### Posts
- `GET /api/posts/`: Retrieve all posts.
- `POST /api/posts/`: Create a new post.
- `GET /api/posts/<id>/`: Retrieve, update, or delete a specific post.

#### Follow/Unfollow
- `POST /api/users/<username>/follow/`: Follow a user.
- `POST /api/users/<username>/unfollow/`: Unfollow a user.
- `GET /api/users/<username>/followers/`: Retrieve a user's followers.
- `GET /api/users/<username>/following/`: Retrieve users a specific user is following.

#### User Actions
- `POST /api/actions/<username>/action/`: Hide or block a user.
- `DELETE /api/actions/<username>/remove_action/`: Remove an action on a user.
- `GET /api/actions/list_actions/`: Retrieve all actions performed by the authenticated user.

#### Feed
- `GET /api/feed/`: Retrieve the personalized feed.

---

### Installation

Follow these steps to set up the project locally:

#### Clone the Repository

```bash
git clone https://github.com/your-repo/social-media-api.git
cd social-media-api
