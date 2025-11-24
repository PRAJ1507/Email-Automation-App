import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export async function uploadContacts(file) {
  const form = new FormData();
  form.append("file", file);
  try {
    const res = await axios.post(`${BASE_URL}/upload-contacts`, form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data;
  } catch (err) {
    throw new Error(err.response?.data?.detail || err.response?.data || err.message);
  }
}

export async function confirmContacts(payload) {
  try {
    const res = await axios.post(`${BASE_URL}/contacts/confirm`, payload);
    return res.data;
  } catch (err) {
    throw new Error(err.response?.data?.detail || err.response?.data || err.message);
  }
}

export async function listEmails(campaignId, status) {
  try {
    const params = { campaign_id: campaignId };
    if (status) params.status = status;
    const res = await axios.get(`${BASE_URL}/emails/`, { params });
    return res.data;
  } catch (err) {
    throw new Error(err.response?.data?.detail || err.response?.data || err.message);
  }
}

export async function updateEmail(emailId, payload) {
  try {
    const res = await axios.put(`${BASE_URL}/emails/${emailId}`, payload);
    return res.data;
  } catch (err) {
    throw new Error(err.response?.data?.detail || err.response?.data || err.message);
  }
}

export async function sendEmails(campaignId, stepNumber) {
  try {
    const res = await axios.post(
      `${BASE_URL}/emails/send`,
      { step_number: stepNumber, send_mode: "immediate" },
      { params: { campaign_id: campaignId } }
    );
    return res.data;
  } catch (err) {
    throw new Error(err.response?.data?.detail || err.response?.data || err.message);
  }
}

export async function getCampaignStatus(campaignId) {
  try {
    const res = await axios.get(`${BASE_URL}/campaigns/${campaignId}`);
    return res.data;
  } catch (err) {
    throw new Error(err.response?.data?.detail || err.response?.data || err.message);
  }
}

export async function listContacts() {
  try {
    const res = await axios.get(`${BASE_URL}/contacts`);
    return res.data;
  } catch (err) {
    throw new Error(err.response?.data?.detail || err.response?.data || err.message);
  }
}

export async function generateEmails(campaignId, contactIds) {
  const payload = { regenerate: true };
  if (contactIds && contactIds.length > 0) {
    payload.contact_ids = contactIds;
  }
  try {
    const res = await axios.post(
      `${BASE_URL}/campaigns/${campaignId}/generate-emails`,
      payload
    );
    return res.data;
  } catch (err) {
    throw new Error(err.response?.data?.detail || err.response?.data || err.message);
  }
}
