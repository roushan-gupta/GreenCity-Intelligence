let latitude = null;
let longitude = null;
let placeName = null;

const userId = localStorage.getItem("user_id");
const name = localStorage.getItem("name");
const role = localStorage.getItem("role");

if (!userId) {
  window.location.href = "index.html";
}

document.getElementById("welcome").innerText = "Welcome, " + name + "! 👋";

// Profile Dropdown Functions
function toggleDropdown() {
  const dropdown = document.getElementById("profileDropdown");
  dropdown.classList.toggle("show");
}

// Close dropdown when clicking outside
window.onclick = function (event) {
  if (!event.target.closest(".profile-dropdown")) {
    const dropdown = document.getElementById("profileDropdown");
    if (dropdown.classList.contains("show")) {
      dropdown.classList.remove("show");
    }
  }
};

// Section Navigation
function showSection(section) {
  // Hide all sections
  document.querySelectorAll(".section-content").forEach((el) => {
    el.classList.remove("active");
  });

  // Close dropdown
  document.getElementById("profileDropdown").classList.remove("show");

  // Show selected section
  if (section === "dashboard") {
    document.getElementById("dashboardSection").classList.add("active");
  } else if (section === "profile") {
    document.getElementById("profileSection").classList.add("active");
    loadProfile();
  } else if (section === "notifications") {
    document.getElementById("notificationsSection").classList.add("active");
    // Mark all notifications as read and reset badge to zero
    markAllNotificationsAsRead();
    // Reload notifications after a short delay to show updated read status
    setTimeout(() => {
      loadNotifications();
    }, 300);
  }
}

// Load Profile Data
function loadProfile() {
  fetch(`http://127.0.0.1:5000/users/${userId}`)
    .then((res) => res.json())
    .then((data) => {
      if (data.message) {
        return;
      }

      document.getElementById("profileNameInput").value = data.name || "";
      document.getElementById("profileEmailInput").value = data.email || "";
      document.getElementById("profileContactInput").value = data.contact_number || "";
      document.getElementById("profileHouseInput").value = data.address_house || "";
      document.getElementById("profileStreetInput").value = data.address_street || "";
      document.getElementById("profileCityInput").value = data.address_city || "";
      document.getElementById("profileStateInput").value = data.address_state || "";
      document.getElementById("profilePincodeInput").value = data.address_pincode || "";
      document.getElementById("profileRoleInput").value = data.role || "Citizen";
      document.getElementById("profileUserIdInput").value = data.user_id || userId;

      localStorage.setItem("name", data.name || "");
      localStorage.setItem("email", data.email || "");
      document.getElementById("welcome").innerText = "Welcome, " + (data.name || name) + "!";
    })
    .catch(() => {
      document.getElementById("profileSaveMsg").innerText = "Failed to load profile";
      document.getElementById("profileSaveMsg").className = "mt-2 text-danger";
    });
}

function refreshUserSummary() {
  fetch(`http://127.0.0.1:5000/users/${userId}`)
    .then((res) => res.json())
    .then((data) => {
      if (data.message) {
        return;
      }
      localStorage.setItem("name", data.name || "");
      localStorage.setItem("email", data.email || "");
      document.getElementById("welcome").innerText = "Welcome, " + (data.name || name) + "!";
    })
    .catch(() => {
      document.getElementById("welcome").innerText = "Welcome, " + (name || "Citizen") + "!";
    });
}

// Load Dashboard Stats (just notification badge)
function loadNotificationCount() {
  // Load unread notification count
  fetch(`http://127.0.0.1:5000/notifications/unread-count?user_id=${userId}`)
    .then((res) => res.json())
    .then((data) => {
      const count = data.unread_count || 0;
      updateNotificationBadge(count);
    })
    .catch(() => {
      updateNotificationBadge(0);
    });
}

// Update notification badge
function updateNotificationBadge(count) {
  const badge = document.getElementById("notificationBadge");
  const dropdownBadge = document.getElementById("dropdownNotificationBadge");
  
  if (count > 0) {
    badge.style.display = "flex";
    badge.innerText = count > 9 ? "9+" : count;
    dropdownBadge.style.display = "inline";
    dropdownBadge.innerText = count;
  } else {
    badge.style.display = "none";
    dropdownBadge.style.display = "none";
  }
}

function saveProfile() {
  const nameValue = document.getElementById("profileNameInput").value.trim();
  const contactValue = document.getElementById("profileContactInput").value.trim();
  const houseValue = document.getElementById("profileHouseInput").value.trim();
  const streetValue = document.getElementById("profileStreetInput").value.trim();
  const cityValue = document.getElementById("profileCityInput").value.trim();
  const stateValue = document.getElementById("profileStateInput").value.trim();
  const pincodeValue = document.getElementById("profilePincodeInput").value.trim();

  if (!nameValue || !contactValue || !houseValue || !streetValue || !cityValue || !stateValue || !pincodeValue) {
    document.getElementById("profileSaveMsg").innerText = "Please fill all fields";
    document.getElementById("profileSaveMsg").className = "mt-2 text-danger";
    return;
  }

  fetch(`http://127.0.0.1:5000/users/${userId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      name: nameValue,
      contact_number: contactValue,
      address_house: houseValue,
      address_street: streetValue,
      address_city: cityValue,
      address_state: stateValue,
      address_pincode: pincodeValue,
    }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.message === "Profile updated successfully") {
        document.getElementById("profileSaveMsg").innerText = data.message;
        document.getElementById("profileSaveMsg").className = "mt-2 text-success";
        localStorage.setItem("name", nameValue);
        document.getElementById("welcome").innerText = "Welcome, " + nameValue + "!";
      } else {
        document.getElementById("profileSaveMsg").innerText = data.message || "Failed to update profile";
        document.getElementById("profileSaveMsg").className = "mt-2 text-danger";
      }
    })
    .catch(() => {
      document.getElementById("profileSaveMsg").innerText = "Failed to update profile";
      document.getElementById("profileSaveMsg").className = "mt-2 text-danger";
    });
}

// Function to get place name from coordinates using OpenStreetMap Nominatim API
async function getPlaceName(lat, lng) {
  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&accept-language=en`
    );
    const data = await response.json();
    
    // Extract district, state, and country from the response
    const address = data.address || {};
    const district = address.city || address.town || address.village || address.county || address.suburb || "";
    const state = address.state || address.region || "";
    const country = address.country || "";
    
    // Build comma-separated location string
    const parts = [district, state, country].filter(part => part.trim() !== "");
    return parts.join(", ") || "Unknown Location";
  } catch (error) {
    console.error("Error fetching place name:", error);
    return "Location";
  }
}

async function selectLocation() {
  if (!navigator.geolocation) {
    alert("Geolocation is not supported by your browser");
    return;
  }

  // Show loading state
  document.getElementById("locationText").innerText = "📍 Detecting location...";
  document.getElementById("locationText").className = "text-info";

  navigator.geolocation.getCurrentPosition(
    async (position) => {
      latitude = position.coords.latitude;
      longitude = position.coords.longitude;

      // Get place name from coordinates
      placeName = await getPlaceName(latitude, longitude);

      // Display location without opening Google Maps
      document.getElementById("locationText").innerText =
        `📍 ${placeName}\n(Lat: ${latitude.toFixed(6)}, Lng: ${longitude.toFixed(6)})`;
      document.getElementById("locationText").className = "alert alert-success";
    },
    (error) => {
      document.getElementById("locationText").innerText = "📌 Location not selected";
      document.getElementById("locationText").className = "text-muted";
      alert("Please allow location access to report incident");
    },
  );
}

// Report incident
function reportIncident() {
  const incident_type = document.getElementById("incident_type").value.trim();
  const description = document.getElementById("description").value.trim();
  
  if (!incident_type) {
    alert("Please enter incident type");
    return;
  }
  
  if (!latitude || !longitude) {
    alert("Please select your current location first");
    return;
  }

  const formData = new FormData();
  formData.append("user_id", userId);
  formData.append("incident_type", incident_type);
  formData.append("description", description);
  formData.append("latitude", latitude);
  formData.append("longitude", longitude);
  formData.append("place_name", placeName || "Unknown Location");

  const image = document.getElementById("image").files[0];
  if (image) {
    formData.append("image", image);
  }

  fetch("http://127.0.0.1:5000/report-incident", {
    method: "POST",
    body: formData,
  })
    .then((res) => res.json())
    .then((data) => {
      document.getElementById("msg").innerText = data.message;
      document.getElementById("msg").className = "mt-2 text-success";
      
      // Clear form
      document.getElementById("incident_type").value = "";
      document.getElementById("description").value = "";
      document.getElementById("image").value = "";
      latitude = null;
      longitude = null;
      placeName = null;
      document.getElementById("locationText").innerText = "📌 Location not selected";
      document.getElementById("locationText").className = "text-muted p-2 mb-3";
      
      // Refresh notification count
      loadNotificationCount();
    })
    .catch((err) => {
      document.getElementById("msg").innerText = "Error submitting incident";
      document.getElementById("msg").className = "mt-2 text-danger";
    });
}

// Load notifications
function loadNotifications() {
  fetch(`http://127.0.0.1:5000/notifications?user_id=${userId}`)
    .then((res) => res.json())
    .then((data) => {
      const ul = document.getElementById("notifications");
      const noNotifications = document.getElementById("noNotifications");
      
      ul.innerHTML = "";
      
      if (data.length === 0) {
        noNotifications.style.display = "block";
        ul.style.display = "none";
      } else {
        noNotifications.style.display = "none";
        ul.style.display = "block";
        
        data.forEach((n) => {
          const li = document.createElement("li");
          li.className = n.is_read ? "list-group-item" : "list-group-item list-group-item-warning";
          
          const messageDiv = document.createElement("div");
          messageDiv.className = "d-flex justify-content-between align-items-start";
          
          const textDiv = document.createElement("div");
          textDiv.innerHTML = `<strong>${n.message}</strong><br><small class="text-muted">${new Date(n.created_at).toLocaleString()}</small>`;
          
          messageDiv.appendChild(textDiv);
          
          if (!n.is_read) {
            const badge = document.createElement("span");
            badge.className = "badge bg-primary";
            badge.innerText = "New";
            messageDiv.appendChild(badge);
          }
          
          li.appendChild(messageDiv);
          ul.appendChild(li);
        });
      }
      
      // Update notification badge
      const unreadCount = data.filter(n => !n.is_read).length;
      updateNotificationBadge(unreadCount);
    })
    .catch((err) => {
      console.error("Error loading notifications:", err);
    });
}

// Mark all notifications as read
function markAllNotificationsAsRead() {
  fetch("http://127.0.0.1:5000/notifications/mark-all-read", {
    method: "PUT",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      user_id: userId
    })
  })
    .then((res) => res.json())
    .then((data) => {
      // Reset badge to zero immediately
      updateNotificationBadge(0);
    })
    .catch((err) => {
      console.error("Error marking notifications as read:", err);
    });
}

// Logout
function logout() {
  localStorage.clear();
  window.location.href = "index.html";
}

// Initialize notification count and load notifications on page load
loadNotificationCount();
refreshUserSummary();
