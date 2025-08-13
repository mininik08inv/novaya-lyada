from django.shortcuts import render
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView


class AllAdvertisement(ListView):
    pass

class ShowAdvertisement(DetailView):
    pass


class UpdateAdvertisement(UpdateView):
    pass


class AddAdvertisement(CreateView):
    pass

class DeleteAdvertisement(DeleteView):
    pass